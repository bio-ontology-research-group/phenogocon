from org.apache.jena.rdf.model import ModelFactory
from org.apache.jena.vocabulary import RDF
from org.semanticweb.elk.owlapi import ElkReasonerFactory
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, \
    SimpleConfiguration, InferenceType
    
from Queue import Queue
from threading import Thread

numThreads = 48


gobasic = "go-basic.obo"
go = "http://purl.obolibrary.org/obo/GO_"
down = ["http://purl.obolibrary.org/obo/PATO_0000462", "http://purl.obolibrary.org/obo/PATO_0000381", "http://purl.obolibrary.org/obo/PATO_0000911", "http://purl.obolibrary.org/obo/PATO_0000297", "http://purl.obolibrary.org/obo/PATO_0001511", "http://purl.obolibrary.org/obo/PATO_0001507"]
abnormal = ["http://purl.obolibrary.org/obo/PATO_0000001"]
up = ["http://purl.obolibrary.org/obo/PATO_0000912"]

pheno2gofile = "pheno2go.txt"


manager = OWLManager.createOWLOntologyManager()
ont = manager.loadOntologyFromOntologyDocument(IRI.create("file:" + gobasic))
fac = manager.getOWLDataFactory()
progressMonitor = ConsoleProgressMonitor()
config = SimpleConfiguration(progressMonitor)
f1 = ElkReasonerFactory()
reasoner = f1.createReasoner(ont, config)
reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY)


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

# begin threading
queue = Queue()
for cl in ont.getClassesInSignature(True):
    queue.put(cl)
print "Queue built. There are %d classes to process." % queue._qsize()

def job(i, q):
    while True:
        cl = q.get()
        size = q._qsize()
        if size % 1000 == 0:
            print "%d entries left in queue" % size
                
        clstring = cl.toString().replace(go, "GO:").replace(">","").replace("<", "")
        for [reg, updown] in [[pr, "up"], [nr, "down"]]:
            c = fac.getOWLObjectSomeValuesFrom(reg, cl)
            for sub in reasoner.getSubClasses(c, False).getFlattened():
                subs = sub.toString().replace(go, "GO:").replace(">","").replace("<", "")
                if subs == "owl:Nothing":
                    continue
                if (subs, updown) not in regmap:
                    regmap[(subs, updown)] = set()
                regmap[(subs, updown)].add(clstring)
                
        q.task_done()

# initiate threads
for i in range(numThreads):
    print "Thread %d initiated" % (i+1)
    t = Thread(target=job, args=(i, queue))
    t.setDaemon(True)
    t.start()

# wait for threads to finish
queue.join()

# build go2pheno
print "Building go2pheno..."
for line in open(pheno2gofile, 'r'):
    tabs = line.strip('\n').split('\t')
    pheno = tabs[0]
    gos = tabs[1].replace(go, "GO:")
    if tabs[2] in down:
        go2pheno[(gos, "down")] = pheno
    if tabs[2] in up:
        go2pheno[(gos, "up")] = pheno
    if tabs[2] in abnormal: # abnormal
        go2pheno[(gos, "abnormal")] = pheno

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

# start writing to file
outlines = []
print "Writing to inferred-phenos..."
for gene in gene2go:
    for gos in gene2go[gene]:
        if (gos, "abnormal") in go2pheno:
            outlines.append("%s\t%s\t%s\t%s\n" % (gene, gos, go2pheno[(gos, "abnormal")], "abnormal"))
        for i in range(2):
            direction = ["up", "down"][i]
            antidirection = ["up", "down"][1-i]
            if (gos, direction) in regmap:
                go2 = regmap[(gos, direction)] # gos up/down-regulates go2
                for g2 in go2:
                    if (g2, antidirection) in go2pheno: # find the decreased go2 phenotype
                        outlines.append("%s\t%s\t%s\t%s\n" % (gene, gos, go2pheno[(g2, antidirection)], antidirection))

outlines.sort() # output file will be in sorted order
with open("inferred-phenos.txt", 'w') as gout:
    for string in outlines:
        gout.write(string)
        
print "Program terminated."