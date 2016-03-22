from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI, AxiomType, ClassExpressionType, OWLQuantifiedRestriction
from org.semanticweb.owlapi.model.parameters import Imports
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, SimpleConfiguration
from org.semanticweb.owlapi.reasoner.structural import StructuralReasonerFactory
from org.semanticweb.owlapi.search import EntitySearcher
from org.semanticweb.owlapi.util import InferredOntologyGenerator, \
    InferredSubClassAxiomGenerator, InferredClassAssertionAxiomGenerator, \
    InferredEquivalentClassAxiomGenerator


owlfiles = ["uberon", "go", "bspo", "zfa", "pato", "cl-basic", "nbo"]

manager = OWLManager.createOWLOntologyManager()
ontset = set()
ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "mp.owl")))
ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "hp.owl")))
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

# for cl in clset:
#     for ax in EntitySearcher.getAnnotationAssertionAxioms(cl, ont):
#         manager.addAxiom(ont_out, ax)

# for owl in owlfiles:
#     print "Processing " + owl
#     ont_temp = manager.loadOntologyFromOntologyDocument(IRI.create("file:" + owl + ".owl"))
#     reasonertemp = f1.createReasoner(ont_temp, config)
#     generatortemp = InferredOntologyGenerator(reasonertemp, [InferredSubClassAxiomGenerator(), InferredClassAssertionAxiomGenerator(), InferredEquivalentClassAxiomGenerator(), InferredSubClassAxiomGenerator()])
#     generatortemp.fillOntology(fac, ont_out)
#     for ax in ont_temp.getTBoxAxioms(Imports.INCLUDED):
#         if not ax.isOfType(AxiomType.DISJOINT_CLASSES):
#             manager.addAxiom(ont_out, ax)
#     for cl in ont_temp.getClassesInSignature(True):
#         for ax in EntitySearcher.getAnnotationAssertionAxioms(cl, ont_temp):
#             manager.addAxiom(ont_out, ax)

print "Building ontology..."


# def formatClassNames(s):
#     s = s.replace("<http://purl.obolibrary.org/obo/","")
#     s = s.replace(">","")
#     s = s.replace("_",":")
#     return s



# id2class = dict() # maps class id to owl class
# id2name = dict()
# for x in clset:
#     aa = formatClassNames(x.toString())
#     if aa not in id2class:
#         id2class[aa] = x
#     for lab in EntitySearcher.getAnnotationObjects(cl, ont, fac.getRDFSLabel()):
#         id2name[cl] = lab.getValue().asLiteral()
#    
# 
# def addAnno(resource, prop, cont):
#     axiom = fac.getOWLAnnotationAssertionAxiom(fac.getOWLAnnotationProperty(prop.getIRI()), resource.getIRI(), cont)
#     manager.addAxiom(ont_out,axiom)
# 
# def create_relation(s):
#     if (s == "part-of"):
#         fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/BFO_0000050"))
#     elif (s == "has-part"):
#         fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/BFO_0000051"))
#     else:
#         fac.getOWLObjectProperty(IRI.create("http://aber-owl.net/#"+s))
# 
# 
# def create_class(s):
#     return fac.getOWLClass(IRI.create(onturi+s))
# 
# def intersect(cl1, cl2):
#     return fac.getOWLObjectIntersectionOf(cl1,cl2)
# 
# def some(r, cl):
#     return fac.getOWLObjectSomeValuesFrom(r,cl)
# 
# def equiv(cl1, cl2):
#     return fac.getOWLEquivalentClassesAxiom(cl1, cl2)
# 
# def subclass(cl1, cl2):
#     return fac.getOWLSubClassOfAxiom(cl1, cl2)

print "%d classes to process" % len(clset)
for cl in clset:
    if "MP_" in cl.toString() or "HP_" in cl.toString():
        q = []
        e = []
#         e2 = []
#         po = []
#         ihp = []
#         modifier = []
#         occursin = []
#         haspart = []
#         during = []
#         hasquality = []
#         centralparticipant = []
#         resultsfrom = []
        
        for cExpr in EntitySearcher.getEquivalentClasses(cl, ont): # OWL Class Expression
            if (not cExpr.isClassExpressionLiteral()) and cExpr.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM:
                c = cExpr
                if c.getProperty() and c.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>":
                    c = c.getFiller().asConjunctSet()
                    for conj in c:
                        if conj.isClassExpressionLiteral():
                            q.append(conj)
                        elif conj.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM:
#                             conj = OWLQuantifiedRestriction(conj) 
#                             
                            if conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0000052>": # inheres-in
                                e.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0002573>": # modifier
#                                  modifier.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0002314>": # inheres in part of (make part-of some E)
#                                 ihp.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0002503>": # towards
#                                 e2.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#has_quality>": # has-quality (make quality of Q)
#                                 hasquality.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#exists_during>": # exists-during (modified/intersect of E2)
#                                 during.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>": # has-part: treat as intersection ( :( )
#                                 haspart.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000050>": # part-of (E and part-of some X)
#                                 po.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#has_central_participant>": # has-central-participant (?)
#                                 centralparticipant.append(conj.getFiller())
#                             elif conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#results_from>": # has-central-participant (?)
#                                 resultsfrom.append(conj.getFiller())
#                             elif conj.getProperty().toString() in ["<http://purl.obolibrary.org/obo/BFO_0000066>","<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#occurs_in>"]: # occurs-in: make modifier to E (E occurs in ...)
#                                 occursin.append(conj.getFiller())
#                             else:
#                                 print "Ignoring: " + cl.toString() + conj.getProperty().toString()
        
        gout = open("pheno2go.txt", 'w')
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
        
gout.close()

print "Program terminated."
