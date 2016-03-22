from org.semanticweb.owlapi.model import IRI
from org.semanticweb.elk.owlapi import ElkReasonerFactory
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, \
    SimpleConfiguration


manager = OWLManager.createOWLOntologyManager()
factory = manager.getOWLDataFactory()
ontset = set()
ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "mp.owl")))
ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "hp.owl")))
ont = manager.createOntology(IRI.create("http://aber-owl.net/phenotype-input.owl"), ontset)

progressMonitor = ConsoleProgressMonitor();
config = SimpleConfiguration(progressMonitor);
reasoner = ElkReasonerFactory().createReasoner(ont, config);

phenos = "MGI_GenePheno.rpt"

def create_class(s):
    return factory.getOWLClass(IRI.create(s))

def formatClassNames(s):
    s = s.replace("http://purl.obolibrary.org/obo/","")
    s = s.replace("<","")
    s = s.replace(">","")
    s = s.replace("_",":")
    return s

mgi2mp = dict()
with open(phenos, 'r') as f:
    for line in f:
        tabs = line.strip('\n').split('\t')
        mp = tabs[4]
        mgi = tabs[6]
        if mgi not in mgi2mp:
            mgi2mp[mgi] = set()
        mgi2mp[mgi].add(mp)
        iri = "http://purl.obolibrary.org/obo/" + mp.replace(":", "_")
        mpclass = create_class(iri)
        subclasses = reasoner.getSubClasses(mpclass, False).getFlattened()
        for subcl in subclasses:
            entry = subcl.toString()
            if "MP" in entry:
                mgi2mp[mgi].add(formatClassNames(entry))
        
hits = 0
misses = 0
unknown = 0    

with open("inferred-phenos.txt", 'r') as f:
    for line in f:
        tabs = line.strip('\n').split('\t')
        mgi = tabs[0]
        mp = formatClassNames(tabs[2])
        if mgi in mgi2mp:
            if mp in mgi2mp[mgi]:
                hits += 1
                if len(tabs) > 3:
                    print mgi, mp
            else:
                misses += 1
        else:
            unknown += 1

print "%d hits, %d misses, %d unknown" % (hits, misses, unknown)
if (hits + misses) > 0:
    print "precision = %f" % (float(hits) / float(hits + misses))
    
print "Program terminated"
