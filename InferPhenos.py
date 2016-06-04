import os

from org.apache.jena.rdf.model import ModelFactory
from org.apache.jena.vocabulary import RDF
from org.semanticweb.elk.owlapi import ElkReasonerFactory
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, \
    SimpleConfiguration, InferenceType
from org.semanticweb.owlapi.search import EntitySearcher

from Queue import Queue
from threading import Thread


numThreads = 48

gobasic = "go.owl"
go = "http://purl.obolibrary.org/obo/GO_"
# down = ["http://purl.obolibrary.org/obo/PATO_0000462", "http://purl.obolibrary.org/obo/PATO_0000381", "http://purl.obolibrary.org/obo/PATO_0000911", "http://purl.obolibrary.org/obo/PATO_0000297", "http://purl.obolibrary.org/obo/PATO_0001511", "http://purl.obolibrary.org/obo/PATO_0001507"]
# abnormal = ["http://purl.obolibrary.org/obo/PATO_0000001"]
# up = ["http://purl.obolibrary.org/obo/PATO_0000912"]

pheno2gofile = "pheno2go.txt"

def create_class(s):
    return fac.getOWLClass(IRI.create(s))

def formatClassNames(s):
    s = s.replace("http://purl.obolibrary.org/obo/", "")
    s = s.replace("<", "")
    s = s.replace(">", "")
    s = s.replace("_", ":")
    return s

manager = OWLManager.createOWLOntologyManager()
ont = manager.loadOntologyFromOntologyDocument(IRI.create("file:" + gobasic))
fac = manager.getOWLDataFactory()
# progressMonitor = ConsoleProgressMonitor()
# config = SimpleConfiguration(progressMonitor)
# f1 = ElkReasonerFactory()
# reasoner = f1.createReasoner(ont, config)
# reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY)

regmap = dict() # maps a 2-item list to set   e.g. [cl1, "down"]:{cl2, cl3, cl4}    cl1 down-regulates cl2, cl3 and cl4
go2pheno = dict() # maps a 2-item list to a string
gene2go = dict() # maps string to set

# other direction
pheno2go = dict()
go2mgi = dict()

class Species:
    name = ""
    filename = ""
    columns = (-1, -1)
    def __init__(self, name, association, columns):
        self.name = name
        self.association = association
        self.columns = columns
        
speciesList = []
# put your species here, each instance is [name, filename, columns (gene, pheno)]
speciesList.append(Species("MP", "gene_association.mgi", (1, 4)))
speciesList.append(Species("HP", "gene_association.goa_human", (2, 4)))
speciesList.append(Species("FYPO", "gene_association.goa_yeast", (2, 4)))
speciesList.append(Species("FBcv", "gene_association.goa_fly", (2, 4)))

# build regmap
print "Building regmap..."
pr = fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/RO_0002213"))
nr = fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/RO_0002212"))

def job(i, q):
    progressMonitor = ConsoleProgressMonitor()
    config = SimpleConfiguration(progressMonitor)
    f1 = ElkReasonerFactory()
    reasoner = f1.createReasoner(ont, config)
    reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY)
    while True:
        cl = q.get()
        size = q._qsize()
        if size % 1000 == 0:
            print "%d entries left in queue" % size
                
        clstring = formatClassNames(cl.toString())
        for [reg, updown] in [[pr, "up"], [nr, "down"]]:
            c = fac.getOWLObjectSomeValuesFrom(reg, cl)
            c = fac.getOWLObjectIntersectionOf(c, create_class("http://purl.obolibrary.org/obo/GO_0065007"))
            
            equiv = reasoner.getEquivalentClasses(c)
            
#             if "0003094" in clstring:
#                 print c
#                 print equiv
#                 for x in reasoner.getSubClasses(c, True).getFlattened():
#                     print EntitySearcher.getEquivalentClasses(x, ont)
            
            for x in equiv:              
                subs = formatClassNames(x.toString())
                if subs == "owl:Nothing":
                    continue
                if (subs, updown) not in regmap:
                    regmap[(subs, updown)] = set()
                regmap[(subs, updown)].add(clstring)
                
        q.task_done()

if os.path.isfile("regmap_data.txt"):
    with open("regmap_data.txt", 'r') as f:
        for line in f:
            (subs, updown, clstring) = line.strip().split('\t')
            if (subs, updown) not in regmap:
                regmap[(subs, updown)] = set()
            regmap[(subs, updown)].add(clstring)
else: # delete regmap data in order to rebuild map
    # begin threading
    queue = Queue()
    for cl in ont.getClassesInSignature(True):
        queue.put(cl)
    print "Queue built. There are %d classes to process." % queue._qsize()
    
    # initiate threads
    for i in range(numThreads):
        print "Thread %d initiated" % (i+1)
        t = Thread(target=job, args=(i, queue))
        t.setDaemon(True)
        t.start()
    
    # wait for threads to finish
    queue.join()
    
    # write to text file, next time we can just load data from text file
    with open("regmap_data.txt", 'w') as g:
        for (subs, updown) in regmap:
            for clstring in regmap[(subs, updown)]:
                g.write("%s\t%s\t%s\n" % (subs, updown, clstring))

# build go2pheno
print "Building go2pheno..."
for line in open(pheno2gofile, 'r'):
    tabs = line.strip('\n').split('\t')
    pheno = tabs[0]
    gos = tabs[1]
    reg = tabs[2]
    if (gos, reg) not in go2pheno:
        go2pheno[(gos, reg)] = set()
    go2pheno[(gos, reg)].add(pheno)

# build gene2go
print "Building gene2go..."
for species in speciesList:
    for line in open(species.association, 'r'):
        if not line or line[0] in "!#":
            continue
        tabs = line.strip('\n').split('\t')
        if len(tabs) > 1:
            gene = tabs[species.columns[0]]
            gos = tabs[species.columns[1]]
            if gene not in gene2go:
                gene2go[gene] = set()
            gene2go[gene].add(gos)

# infer
outlines = set()
print "Making inferences..."
for gene in gene2go:
    for gos in gene2go[gene]:
        if (gos, "abnormal") in go2pheno:
            for pheno in go2pheno[(gos, "abnormal")]:
                outlines.add("%s\t%s\t%s\t%s\t%s\n" % (gene, pheno, "abnormal", gos, "NONE"))
        for i in range(2):
            direction = ["up", "down"][i]
            antidirection = ["up", "down"][1-i]
            if (gos, direction) in regmap:
                go2 = regmap[(gos, direction)] # gos up/down-regulates go2
                for g2 in go2:
                    if (g2, antidirection) in go2pheno: # find the decreased go2 phenotype
                        for pheno in go2pheno[(g2, antidirection)]:
                            outlines.add("%s\t%s\t%s\t%s\t%s\n" % (gene, pheno, antidirection, gos, g2))
                            
print "%d inferences made. Writing to file..." % len(outlines)
with open("inferred-phenos.txt", 'w') as gout:
    for string in outlines:
        gout.write(string)
        
# negated inferences
negoutlines = set()
print "Making negated inferences..."
for gene in gene2go:
    for gos in gene2go[gene]:
        for i in range(2):
            direction = ["up", "down"][i]
            antidirection = ["up", "down"][1-i]
            if (gos, direction) in regmap:
                go2 = regmap[(gos, direction)] # gos up/down-regulates go2
                for g2 in go2:
                    if (g2, direction) in go2pheno: # find the decreased go2 phenotype. Negate
                        for pheno in go2pheno[(g2, direction)]:
                            negoutlines.add("%s\t%s\t%s\t%s\t%s\n" % (gene, pheno, direction, gos, g2))
                            
print "%d negated inferences made. Writing to file..." % len(negoutlines)
with open("neg-inferred-phenos.txt", 'w') as gout:
    for string in negoutlines:
        gout.write(string)
        
print "Program terminated."