from org.semanticweb.elk.owlapi import ElkReasonerFactory
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI, AxiomType, ClassExpressionType, OWLQuantifiedRestriction
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, SimpleConfiguration
from org.semanticweb.owlapi.search import EntitySearcher

from Queue import Queue
from threading import Thread


# from org.semanticweb.owlapi.model.parameters import Imports
# from org.semanticweb.owlapi.reasoner.structural import StructuralReasonerFactory
down = ["PATO:0000462", "PATO:0000381", "PATO:0000911", "PATO:0000297", "PATO:0001511", "PATO:0001507"]
abnormal = ["PATO:0000001"]
up = ["PATO:0000912"]

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


def job(i, q):
    progressMonitor = ConsoleProgressMonitor()
    config = SimpleConfiguration(progressMonitor)
    reasoner = ElkReasonerFactory().createReasoner(ont, config)
    while True:
        (goclass, pato) = q.get()
        size = q._qsize()
        if size % 1000 == 0:
            print "%d entries left in queue" % size
               
        temp = fac.getOWLObjectSomeValuesFrom(create_relation("inheres-in"), goclass)
        temppato = fac.getOWLObjectSomeValuesFrom(create_relation("has-modifier"), create_class(rev_formatClassNames(abnormal[0])))
        temp = fac.getOWLObjectIntersectionOf(temppato, temp)
        temp = fac.getOWLObjectIntersectionOf(create_class(rev_formatClassNames(pato)), temp)
        temp = fac.getOWLObjectSomeValuesFrom(create_relation("has-part"), temp)
        
#             print temp
        subclasses = reasoner.getSubClasses(temp, True).getFlattened()
#             if len(subclasses) > 1:
#                 print goclass, pato, subclasses
        for cl in subclasses:
            if "Nothing" in cl.toString():
                continue
            if cl.toString() in closed:
                continue
            closed.add(cl.toString())
            regout = ""
            if pato in up:
                regout = "up"
            elif pato in down:
                regout = "down"
            elif pato in abnormal:
                regout = "abnormal"
                
            output.append(((formatClassNames(cl.toString()), formatClassNames(goclass.toString()), regout)))
            
        q.task_done()


# owlfiles = ["uberon", "go", "bspo", "zfa", "pato", "cl-basic", "nbo"]
owlfiles = ["mp", "hp", "dpo", "fypo", "apo"]

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
    # ontset = set()
    # for (owl, prefix) in owlfiles:
    #     print "Processing " + owl
    #     ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + owl + ".owl")))
    # ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "go.owl")))
    # ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "pato.owl")))
    # ont = manager.createOntology(IRI.create("http://aber-owl.net/phenotype-input.owl"), ontset)
    
    progressMonitor = ConsoleProgressMonitor()
    config = SimpleConfiguration(progressMonitor)
    # f1 = StructuralReasonerFactory()
    reasoner = ElkReasonerFactory().createReasoner(ont, config)
    
    # clset = ont.getClassesInSignature(True)
    
    queue = Queue()
    
    counter = 0
    print "Checking query subclasses for %s..." % owl
    for goclass in goset:   
        for pato in (up + down + abnormal):
            queue.put((goclass, pato))
            
    print "Queue built. There are %d classes to process." % queue._qsize()
    
    # initiate threads
    for i in range(numThreads):
        print "Thread %d initiated" % (i+1)
        t = Thread(target=job, args=(i, queue))
        t.setDaemon(True)
        t.start()
    
    # wait for threads to finish
    queue.join()

# print "%d classes to process" % len(clset)
# for cl in clset:
#     s = cl.toString()
#     if any([prefix in s for (owl, prefix) in owlfiles]) or "FBbt" in s:
#         q = []
#         e = []
#         
#         for cExpr in EntitySearcher.getEquivalentClasses(cl, ont): # OWL Class Expression
#             
#             if (not cExpr.isClassExpressionLiteral()) and cExpr.getClassExpressionType() in (ClassExpressionType.OBJECT_SOME_VALUES_FROM, ClassExpressionType.OBJECT_INTERSECTION_OF):
#                 c = cExpr
#                 print cl.toString(), cExpr.toString()
#                 ctemp = []
#                 if c.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM and c.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>":  # has-part
#                     ctemp = c.getFiller().asConjunctSet()
#                 elif c.getClassExpressionType() == ClassExpressionType.OBJECT_INTERSECTION_OF:
#                     ctemp = c.asConjunctSet()
# #                     for x in c.asConjunctSet():
# #                         if x.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM and x.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>":
# #                         ctemp += x.getFiller().asConjunctSet()
# #                             print ctemp
#                 for conj in ctemp:
#                     if conj.isClassExpressionLiteral():
#                         q.append(conj)
#                     elif conj.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM:
# #                             conj = OWLQuantifiedRestriction(conj) 
# #                             
#                         if conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0000052>": # inheres-in
#                             e.append(conj.getFiller())
# 
#         
#         scl, sgo, spheno = cl.toString(), "", ""
#         scl = scl[1:len(scl)-1]
#         if e:
#             estring = e[0].toString()
#             pos = estring.find('<')
#             pos1 = estring.find('>')
#             sgo = estring[pos + 1:pos1]
#         if q:
#             spheno = q[0].toString()
#             spheno = spheno[1:len(spheno)-1]
#         if sgo and spheno:
#             gout.write("%s\t%s\t%s\n" % (scl, sgo, spheno))
#     else:
#         pass
#         print cl.toString()

with open("pheno2go.txt", 'w') as gout:
    for triplet in output:
        gout.write("%s\t%s\t%s\n" % triplet)

print "Program terminated."
