from org.semanticweb.elk.owlapi import ElkReasonerFactory
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI, AxiomType, ClassExpressionType, OWLQuantifiedRestriction
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, SimpleConfiguration
from org.semanticweb.owlapi.search import EntitySearcher

from Queue import Queue
from threading import Thread

# from org.semanticweb.owlapi.model.parameters import Imports
# from org.semanticweb.owlapi.reasoner.structural import StructuralReasonerFactory

# quality = ["PATO:0000001"]
# down = ["PATO:0002301", "PATO:0000462", "PATO:0000381", "PATO:0000911", "PATO:0000297", "PATO:0001511", "PATO:0001507", "PATO:0001552", "PATO:0001783", "PATO:0001997", "PATO:0002018"]
# up = ["PATO:0000380", "PATO:0000470", "PATO:0000912", "PATO:0001551", "PATO:0001782", "PATO:0002017", "PATO:0002300"]
# abnormal = ["PATO:0000460"]
# fypo_pheno = "FYPO:0000001"

quality = ["PATO:0000001"]
abnormal = ["PATO:0000460"]
down = ["PATO:0000297", "PATO:0000381", "PATO:0000462", "PATO:0000911", "PATO:0001507", "PATO:0001511"]
up = ["PATO:0000912"]
fypo_pheno = "FYPO:0000001"

manager = OWLManager.createOWLOntologyManager()
fac = manager.getOWLDataFactory()

output = []

numThreads = 48


def create_class(s):
    return fac.getOWLClass(IRI.create(s))


def create_relation(s):
    if s == "inheres-in":
        istring = "http://purl.obolibrary.org/obo/RO_0000052"
    elif s == "has-part":
        istring = "http://purl.obolibrary.org/obo/BFO_0000051"
    elif s == "has-modifier":
        istring = "http://purl.obolibrary.org/obo/RO_0002573"
    elif s == "inheres-in-part-of":
        istring = "http://purl.obolibrary.org/obo/RO_0002314"
    else:
        raise Exception
#         istring = "http://phenomebrowser.net/#" + s
    return fac.getOWLObjectProperty(IRI.create(istring))


def formatClassNames(s):
    s = s.replace("http://purl.obolibrary.org/obo/","")
    s = s.replace("<","")
    s = s.replace(">","")
    s = s.replace("_",":")
    return s


def rev_formatClassNames(s):
    s = s.replace(":", "_")
    s = "http://purl.obolibrary.org/obo/" + s
    return s


def job(i, q, owl, ont):
    global closed
    progressMonitor = ConsoleProgressMonitor()
    config = SimpleConfiguration(progressMonitor)
    reasoner = ElkReasonerFactory().createReasoner(ont, config)
    while True:
        goclass = q.get()
        size = q._qsize()
        if size % 1000 == 0:
            print "%d entries left in queue" % size
            
        if owl in ["mp", "hp"]:
            temp = fac.getOWLObjectSomeValuesFrom(create_relation("inheres-in"), goclass)
            temppato = fac.getOWLObjectSomeValuesFrom(create_relation("has-modifier"), create_class(rev_formatClassNames(abnormal[0])))
            temp = fac.getOWLObjectIntersectionOf(temppato, temp)
            
            temp1 = fac.getOWLObjectIntersectionOf(create_class(rev_formatClassNames(quality[0])), temp)
            query = fac.getOWLObjectSomeValuesFrom(create_relation("has-part"), temp1)
            
        elif owl == "fypo":
            temp = fac.getOWLObjectSomeValuesFrom(create_relation("inheres-in-part-of"), goclass)
            query = fac.getOWLObjectIntersectionOf(temp, create_class(rev_formatClassNames(quality[0])))
            
        subclasses = reasoner.getSubClasses(query, True).getFlattened()
        if len(subclasses) > 1:
            for cl in subclasses:
                if any([x in cl.toString() for x in ["Nothing", "GO"]]):
                    continue
                pato, regout = "", ""
                
                done = False
                for c in EntitySearcher.getEquivalentClasses(cl, ont): # OWL Class Expression
                    if c.isClassExpressionLiteral():
                        continue

                    if c.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM:
                        if c.getProperty() and c.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>":
                            ctemp = c.getFiller().asConjunctSet()
                            for conj in ctemp:
                                if conj.isClassExpressionLiteral():
                                    pato = formatClassNames(conj.toString())
                                    done = True
                                    break
                    elif c.getClassExpressionType() == ClassExpressionType.OBJECT_INTERSECTION_OF:
                        ctemp = c.asConjunctSet()
                        for x in ctemp:
                            if x.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM and x.getProperty().toString() == "<http://purl.obolibrary.org/obo/fypo#qualifier>":
                                ctemp2 = x.getFiller().asConjunctSet()
                                for conj in ctemp2:
                                    if conj.isClassExpressionLiteral():
                                        pato = formatClassNames(conj.toString())
                                        done = True
                                        break
                            if done:
                                break
                    if done:
                        break
                
                if pato in up:
                    regout = "up"
                elif pato in down:
                    regout = "down"
                elif pato in quality + abnormal:
                    regout = "abnormal"
                
                if regout:    
                    output.append(((formatClassNames(cl.toString()), formatClassNames(goclass.toString()), regout)))
    
        q.task_done()


# owlfiles = ["mp", "hp", "dpo", "fypo", "apo"]
owlfiles = ["mp", "hp", "fypo"]

go_ont = manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "go.owl"))
pato_ont = manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "pato.owl"))

goset = go_ont.getClassesInSignature(True)
print "%d GO classes" % len(goset)
    
# Open output file
closed = set()

for owl in owlfiles:
    ontset = set()
    ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + owl + ".owl")))
    ontset.add(go_ont)
    ontset.add(pato_ont)
    
    ont = manager.createOntology(IRI.create("http://aber-owl.net/phenotype-input-%s.owl" % owl), ontset)
    
    progressMonitor = ConsoleProgressMonitor()
    config = SimpleConfiguration(progressMonitor)
    reasoner = ElkReasonerFactory().createReasoner(ont, config)
    
    queue = Queue()
    
    counter = 0
    print "Checking query subclasses for %s..." % owl
    for goclass in goset:
        queue.put(goclass)
            
    print "Queue built. There are %d classes to process." % queue._qsize()
    
    # initiate threads
    for i in range(numThreads):
        print "Thread %d initiated" % (i+1)
        t = Thread(target=job, args=(i, queue, owl, ont))
        t.setDaemon(True)
        t.start()
    
    # wait for threads to finish
    queue.join()

with open("pheno2go.txt", 'w') as gout:
    for triple in output:
        gout.write("%s\t%s\t%s\n" % triple)

print "Program terminated."
