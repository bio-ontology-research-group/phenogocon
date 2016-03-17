from org.apache.jena.rdf.model import ModelFactory
from org.apache.jena.vocabulary import RDF
from org.semanticweb.elk.owlapi import ElkReasonerFactory
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, \
    SimpleConfiguration, InferenceType
    
from Queue import Queue
from threading import Thread

numThreads = 24

# dir = "/home/mencella/borg/mouse_phenotypes/"
gobasic = "go-basic.obo"
go = "http://purl.obolibrary.org/obo/GO_"
down = ["http://purl.obolibrary.org/obo/PATO_0000462", "http://purl.obolibrary.org/obo/PATO_0000381", "http://purl.obolibrary.org/obo/PATO_0000911", "http://purl.obolibrary.org/obo/PATO_0000297", "http://purl.obolibrary.org/obo/PATO_0001511", "http://purl.obolibrary.org/obo/PATO_0001507"]
up = ["http://purl.obolibrary.org/obo/PATO_0000912"]
go_annos = "gene_association.mgi"
phenos = "MGI_GenePheno.rpt"
pheno2go = "pheno2go.txt"


manager = OWLManager.createOWLOntologyManager()
ont_in = manager.loadOntologyFromOntologyDocument(IRI.create("file:" + gobasic))
fac = manager.getOWLDataFactory()
progressMonitor = ConsoleProgressMonitor()
config = SimpleConfiguration(progressMonitor)
f1 = ElkReasonerFactory()
reasoner = f1.createReasoner(ont_in, config)
reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY)

regmap = dict() # maps a 2-item list to set
gosmap = dict() # maps a 2-item list to a string
mgi2go = dict() # maps string to set

# build regmap
print "Building regmap..."
pr = fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/RO_0002213"))
nr = fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/RO_0002212"))

# begin threading
queue = Queue()
for cl in ont_in.getClassesInSignature(True):
    queue.put(cl)
#     if queue._qsize() >= 500:
#         break
print "Queue built. There are %d classes to process." % queue._qsize()

def job(i, q):
    while True:
        cl = q.get()
        size = q._qsize()
        if size % 1000 == 0:
            print "%d entries left in queue" % size
                
        clstring = cl.toString().replace("<http://purl.obolibrary.org/obo/GO_","GO:").replace(">","")
        for [reg, updown] in [[pr, "up"], [nr, "down"]]:
            c = fac.getOWLObjectSomeValuesFrom(reg, cl)
            for sub in reasoner.getSubClasses(c, False).getFlattened():
                subs = sub.toString().replace("<http://purl.obolibrary.org/obo/GO_","GO:").replace(">","")
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
    
queue.join()

# build gosmap
print "Building gosmap..."
for line in open(pheno2go, 'r'):
    tabs = line.strip('\n').split('\t')
    mp = tabs[0]
    gos = tabs[1].replace(go, "GO:")
    if tabs[2] in down:
        gosmap[(gos, "down")] = mp
    if tabs[2] in up:
        gosmap[(gos, "up")] = mp
    if tabs[2] == "http://purl.obolibrary.org/obo/PATO_0000001": # abnormal
        gosmap[(gos, "abnormal")] = mp

# build mgi2go
print "Building mgi2go..."
for line in open(go_annos, 'r'):
    tabs = line.strip('\n').split('\t')
    if len(tabs) > 1:
        mgi = tabs[1]
        gos = tabs[4]
        if mgi not in mgi2go:
            mgi2go[mgi] = set()
        mgi2go[mgi].add(gos)

# start writing to file
gout = open("inferred-phenos.txt", 'w')
print "Writing to inferred-phenos..."
for mgi in mgi2go:
    for gos in mgi2go[mgi]:
        if (gos, "abnormal") in gosmap:
            gout.write("%s\t%s\t%s\n" % (mgi, gos, gosmap[(gos, "abnormal")]))
        for i in range(2):
            direction = ["up", "down"][i]
            antidirection = ["up", "down"][1-i]
            if (gos, direction) in regmap:
                go2 = regmap[(gos, direction)] # gos up/down-regulates go2
                for g2 in go2:
                    if (g2, antidirection) in gosmap: # find the decreased go2 phenotype
                        gout.write("%s\t%s\t%s\t%s\n" % (mgi, gos, gosmap[(g2, antidirection)], antidirection))

gout.close()
print "Program terminated."