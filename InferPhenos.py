import os

# from org.apache.jena.rdf.model import ModelFactory
# from org.apache.jena.vocabulary import RDF
from org.semanticweb.elk.owlapi import ElkReasonerFactory
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI, OWLLiteral
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
pheno2gofile_equiv = "pheno2go_equiv.txt"

def create_class(s):
    return fac.getOWLClass(IRI.create(s))

def formatClassNames(s):
    s = s.replace("http://purl.obolibrary.org/obo/", "")
    s = s.replace("<", "")
    s = s.replace(">", "")
    s = s.replace("_", ":")
    return s

def rev_formatClassNames(s):
    s = s.replace(":", "_")
    s = "http://purl.obolibrary.org/obo/" + s
    return s

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
go2pheno_equiv = dict()
gene2go = dict() # maps string to set

# other direction
pheno2go = dict()
go2mgi = dict()

class Species:
    name = ""
    filename = ""
    owl = ""
    columns = (-1, -1)
    def __init__(self, name, owl, association, columns):
        self.name = name
        self.association = association
        self.columns = columns

speciesList = []
# put your species here, each instance is [name, filename, columns (gene, pheno)]
#speciesList.append(Species("MP", "mp", "gene_association.mgi", (1, 4)))
speciesList.append(Species("HP", "hp", "gene_association.goa_human", (2, 4)))
#speciesList.append(Species("FYPO", "fypo", "gene_association.goa_yeast", (2, 4)))
#speciesList.append(Species("FBcv", "dpo", "gene_association.goa_fly", (2, 4)))

# pheno ontologies
# ontset = set()
# for species in speciesList:
#     ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + species.owl + ".owl")))
#
# phenos_ont = manager.createOntology(IRI.create("http://aber-owl.net/phenotypes.owl"), ontset)


# build id map
id2label = dict()
owlfiles = ["go", "hp"]# "mp", "hp", "fypo"]
ontset = set()
for owl in owlfiles:
    manager1 = OWLManager.createOWLOntologyManager()
    ont1 = manager1.loadOntologyFromOntologyDocument(IRI.create("file:" + owl + ".owl"))
    for cl in ont1.getClassesInSignature(True):
        clid = formatClassNames(cl.toString())
        for anno in EntitySearcher.getAnnotations(cl.getIRI(), ont1):
#             s = anno.getProperty().toStringID()
#             if s == "http://www.geneontology.org/formats/oboInOwl#hasSynonym":
#             if isinstance(anno.getValue(), OWLLiteral):
            if anno.getProperty().isLabel():
                id2label[clid] = anno.getValue().getLiteral()
                break


def idtolabel(classid):
    global id2label
#     return classid
    if classid in id2label:
        return id2label[classid]
    else:
        return classid


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

for line in open(pheno2gofile_equiv, 'r'):
    tabs = line.strip('\n').split('\t')
    pheno = tabs[0]
    gos = tabs[1]
    reg = tabs[2]
    if "Nothing" in pheno:
        continue
    if (gos, reg) not in go2pheno_equiv:
        go2pheno_equiv[(gos, reg)] = set()
    go2pheno_equiv[(gos, reg)].add(pheno)

# build gene2go
print "Building gene2go..."
for species in speciesList:
    for line in open(species.association, 'r'):
        if not line or line[0] in "!#":
            continue
        tabs = line.strip('\n').split('\t')
        if tabs[6] == "ND":
            continue
#         print tabs
        if len(tabs) > 1:
            gene = tabs[species.columns[0]]
            gos = tabs[species.columns[1]]
            if gene not in gene2go:
                gene2go[gene] = set()
            gene2go[gene].add(gos)


# build inferences
subclasses_output = [[], []]
predictions = [[], []]

print "Making inferences..."

for k in range(2): # decides whether we find matches or contradictions
    for gene in gene2go:
        for gos in gene2go[gene]:
            done = False
            ancestor_queue = Queue()
            ancestor_queue.put(gos)
            while not ancestor_queue.empty():
                ancestor = ancestor_queue.get()
                ascend = False # whether we need to go up to the parent levels
                if (ancestor, "abnormal") in go2pheno:
                    for pheno in go2pheno[(ancestor, "abnormal")]:
                        subclasses_output[k].append(("%s\t"*7 + '\n') % (gene, pheno, "abnormal", ancestor, "NONE", idtolabel(pheno), idtolabel(ancestor)))
                        ascend = False
                if (ancestor, "abnormal") in go2pheno_equiv:
                    for pheno in go2pheno_equiv[(ancestor, "abnormal")]:
                        predictions[k].append(("%s\t"*7 + '\n') % (gene, pheno, "abnormal", ancestor, "NONE", idtolabel(pheno), idtolabel(ancestor)))
                for i in range(2):
                    direction = ["up", "down"][i]
                    antidirection = ["up", "down"][1-i-k] # for k=1, will be same as direction
                    if (ancestor, direction) in regmap:
                        go2 = regmap[(ancestor, direction)] # gos up/down-regulates go2
                        for g2 in go2:
                            if (g2, antidirection) in go2pheno: # find the decreased go2 phenotype
                                for pheno in go2pheno[(g2, antidirection)]:
                                    subclasses_output[k].append(("%s\t"*8 + '\n') % (gene, pheno, antidirection, ancestor, g2, idtolabel(pheno), idtolabel(ancestor), idtolabel(g2)))
                                    ascend = False
                            if (g2, antidirection) in go2pheno_equiv:
                                for pheno in go2pheno_equiv[(g2, antidirection)]:
                                    predictions[k].append(("%s\t"*8 + '\n') % (gene, pheno, antidirection, ancestor, g2, idtolabel(pheno), idtolabel(ancestor), idtolabel(g2)))
                if ascend:
                    # replace go class with its ancestor, until reach Thing
                    query = create_class(rev_formatClassNames(ancestor))
                    parents = list(reasoner.getSuperClasses(query, True).getFlattened())
                    # print gos, ancestor, parents
                    for parent in parents:
                        if "Thing" not in parent.toString():
                            ancestor_queue.put(formatClassNames(parent.toString()))


print "%d subclasses inferred. Writing to file..." % len(subclasses_output[0])
subclasses_output[0].sort()
with open("inferred_subclasses.txt", 'w') as gout:
    for string in subclasses_output[0]:
        gout.write(string)

print "%d predictions made. Writing to file..." % len(predictions[0])
predictions[0].sort()
with open("predictions.txt", 'w') as gout:
    for string in predictions[0]:
        gout.write(string)

print "%d negated subclasses inferred. Writing to file..." % len(subclasses_output[1])
subclasses_output[1].sort()
with open("neg_inferred_subclasses.txt", 'w') as gout:
    for string in subclasses_output[1]:
        gout.write(string)

print "%d negated predictions made. Writing to file..." % len(predictions[1])
predictions[1].sort()
with open("neg_predictions.txt", 'w') as gout:
    for string in predictions[1]:
        gout.write(string)


print "Program terminated."
