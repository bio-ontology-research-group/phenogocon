from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI, AxiomType, ClassExpressionType, OWLQuantifiedRestriction
# from org.semanticweb.owlapi.model.parameters import Imports
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, SimpleConfiguration
from org.semanticweb.owlapi.reasoner.structural import StructuralReasonerFactory
from org.semanticweb.owlapi.search import EntitySearcher


# owlfiles = ["uberon", "go", "bspo", "zfa", "pato", "cl-basic", "nbo"]
owlfiles = [("mp", "MP_"), ("hp", "HP_"), ("dpo", "FBcv_"), ("fypo", "FYPO_"), ("apo", "unknown")]


manager = OWLManager.createOWLOntologyManager()
ontset = set()
for (owl, prefix) in owlfiles:
    print "Processing " + owl
    ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + owl + ".owl")))

# for owl in owlfiles:
#     print "Processing " + owl
#     ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + owl + ".owl")))
    
ont = manager.createOntology(IRI.create("http://aber-owl.net/phenotype-input.owl"), ontset)

# ont_out = manager.createOntology(IRI.create("http://aber-owl.net/phenotype.owl"))
onturi = "http://aber-owl.net/phenotype.owl#"

fac = manager.getOWLDataFactory()
progressMonitor = ConsoleProgressMonitor()
config = SimpleConfiguration(progressMonitor)
f1 = StructuralReasonerFactory()
reasoner = f1.createReasoner(ont, config)
# reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY)

# generator = InferredOntologyGenerator(reasoner, [InferredSubClassAxiomGenerator()])
# generator.fillOntology(fac, ont_out)

clset = ont.getClassesInSignature(True)


gout = open("pheno2go.txt", 'w')

print "%d classes to process" % len(clset)
for cl in clset:
    s = cl.toString()
    if any([prefix in s for (owl, prefix) in owlfiles]) or "FBbt" in s:
        q = []
        e = []
        
        for cExpr in EntitySearcher.getEquivalentClasses(cl, ont): # OWL Class Expression
            
            if (not cExpr.isClassExpressionLiteral()) and cExpr.getClassExpressionType() in (ClassExpressionType.OBJECT_SOME_VALUES_FROM, ClassExpressionType.OBJECT_INTERSECTION_OF):
                c = cExpr
#                 print cl.toString(), cExpr.toString()
                ctemp = []
                if c.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM and c.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>":  # has-part
                    ctemp = c.getFiller().asConjunctSet()
                elif c.getClassExpressionType() == ClassExpressionType.OBJECT_INTERSECTION_OF:
                    ctemp = c.asConjunctSet()
#                     for x in c.asConjunctSet():
#                         if x.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM and x.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>":
#                         ctemp += x.getFiller().asConjunctSet()
#                             print ctemp
                for conj in ctemp:
                    if conj.isClassExpressionLiteral():
                        q.append(conj)
                    elif conj.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM:
#                             conj = OWLQuantifiedRestriction(conj) 
#                             
                        if conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0000052>": # inheres-in
                            e.append(conj.getFiller())

        
        scl, sgo, spheno = cl.toString(), "", ""
        scl = scl[1:len(scl)-1]
        if e:
            estring = e[0].toString()
            pos = estring.find('<')
            pos1 = estring.find('>')
            sgo = estring[pos + 1:pos1]
        if q:
            spheno = q[0].toString()
            spheno = spheno[1:len(spheno)-1]
        if sgo and spheno:
            gout.write("%s\t%s\t%s\n" % (scl, sgo, spheno))
    else:
        pass
#         print cl.toString()
gout.close()

print "Program terminated."
