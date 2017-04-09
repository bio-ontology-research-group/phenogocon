@Grapes([
          @Grab(group='org.semanticweb.elk', module='elk-owlapi', version='0.4.2'),
          @Grab(group='net.sourceforge.owlapi', module='owlapi-api', version='4.1.0'),
          @Grab(group='net.sourceforge.owlapi', module='owlapi-apibinding', version='4.1.0'),
          @Grab(group='net.sourceforge.owlapi', module='owlapi-impl', version='4.1.0'),
          @Grab(group='net.sourceforge.owlapi', module='owlapi-parsers', version='4.1.0'),
          @GrabConfig(systemClassLoader=true)
        ])

import org.semanticweb.owlapi.model.parameters.*
import org.semanticweb.elk.owlapi.ElkReasonerFactory;
import org.semanticweb.elk.owlapi.ElkReasonerConfiguration
import org.semanticweb.elk.reasoner.config.*
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.reasoner.*
import org.semanticweb.owlapi.reasoner.structural.StructuralReasoner
import org.semanticweb.owlapi.vocab.OWLRDFVocabulary;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.io.*;
import org.semanticweb.owlapi.owllink.*;
import org.semanticweb.owlapi.util.*;
import org.semanticweb.owlapi.search.*;
import org.semanticweb.owlapi.manchestersyntax.renderer.*;
import org.semanticweb.owlapi.reasoner.structural.*

def fout = new PrintWriter(new BufferedWriter(new FileWriter("go-to-pheno.txt")))

OWLOntologyManager manager = OWLManager.createOWLOntologyManager()
def ontset = new TreeSet()
ontset.add(manager.loadOntologyFromOntologyDocument(new File("MP_5.ont")))
ontset.add(manager.loadOntologyFromOntologyDocument(new File("HP_11.ont")))
OWLOntology ont = manager.createOntology(IRI.create("http://aber-owl.net/phenotype-input.owl"), ontset)

OWLOntology outont = manager.createOntology(IRI.create("http://aber-owl.net/phenotype.owl"))
def onturi = "http://aber-owl.net/phenotype.owl#"

OWLDataFactory fac = manager.getOWLDataFactory()
ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
StructuralReasonerFactory f1 = new StructuralReasonerFactory()
OWLReasoner reasoner = f1.createReasoner(ont,config)
//reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY)

InferredOntologyGenerator generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator()])
generator.fillOntology(fac, outont)

ont.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationAssertionAxioms(cl, ont).each { ax ->
    manager.addAxiom(outont, ax)
  }
}

println "Processing uberon"
OWLOntology ont2 = manager.loadOntologyFromOntologyDocument(IRI.create("http://purl.obolibrary.org/obo/uberon.owl"))
reasoner = f1.createReasoner(ont2, config)
generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator(), new InferredClassAssertionAxiomGenerator(), new InferredEquivalentClassAxiomGenerator(), new InferredSubClassAxiomGenerator()])
generator.fillOntology(fac, outont)
ont2.getTBoxAxioms(Imports.INCLUDED).each { ax ->
  if (! (ax.isOfType(AxiomType.DISJOINT_CLASSES))) {
    manager.addAxiom(outont, ax)
  }
}
ont2.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationAssertionAxioms(cl, ont2).each { ax ->
    manager.addAxiom(outont, ax)
  }
}
println "Processing go"
ont2 = manager.loadOntologyFromOntologyDocument(IRI.create("http://purl.obolibrary.org/obo/go.owl"))
reasoner = f1.createReasoner(ont2, config)
generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator(), new InferredClassAssertionAxiomGenerator(), new InferredEquivalentClassAxiomGenerator(), new InferredSubClassAxiomGenerator()])
generator.fillOntology(fac, outont)
ont2.getTBoxAxioms(Imports.INCLUDED).each { ax ->
  if (! (ax.isOfType(AxiomType.DISJOINT_CLASSES))) {
    manager.addAxiom(outont, ax)
  }
}
ont2.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationAssertionAxioms(cl, ont2).each { ax ->
    manager.addAxiom(outont, ax)
  }
}
println "Processing bspo"
ont2 = manager.loadOntologyFromOntologyDocument(IRI.create("http://purl.obolibrary.org/obo/bspo.owl"))
reasoner = f1.createReasoner(ont2, config)
generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator(), new InferredClassAssertionAxiomGenerator(), new InferredEquivalentClassAxiomGenerator(), new InferredSubClassAxiomGenerator()])
generator.fillOntology(fac, outont)
ont2.getTBoxAxioms(Imports.INCLUDED).each { ax ->
  if (! (ax.isOfType(AxiomType.DISJOINT_CLASSES))) {
    manager.addAxiom(outont, ax)
  }
}
ont2.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationAssertionAxioms(cl, ont2).each { ax ->
    manager.addAxiom(outont, ax)
  }
}
println "Processing zfa"
ont2 = manager.loadOntologyFromOntologyDocument(IRI.create("http://purl.obolibrary.org/obo/zfa.owl"))
reasoner = f1.createReasoner(ont2, config)
generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator(), new InferredClassAssertionAxiomGenerator(), new InferredEquivalentClassAxiomGenerator(), new InferredSubClassAxiomGenerator()])
generator.fillOntology(fac, outont)
ont2.getTBoxAxioms(Imports.INCLUDED).each { ax ->
  if (! (ax.isOfType(AxiomType.DISJOINT_CLASSES))) {
    manager.addAxiom(outont, ax)
  }
}
ont2.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationAssertionAxioms(cl, ont2).each { ax ->
    manager.addAxiom(outont, ax)
  }
}
println "Processing pato"
ont2 = manager.loadOntologyFromOntologyDocument(IRI.create("http://purl.obolibrary.org/obo/pato.owl"))
reasoner = f1.createReasoner(ont2, config)
generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator(), new InferredClassAssertionAxiomGenerator(), new InferredEquivalentClassAxiomGenerator(), new InferredSubClassAxiomGenerator()])
generator.fillOntology(fac, outont)
ont2.getTBoxAxioms(Imports.INCLUDED).each { ax ->
  if (! (ax.isOfType(AxiomType.DISJOINT_CLASSES))) {
    manager.addAxiom(outont, ax)
  }
}
ont2.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationAssertionAxioms(cl, ont2).each { ax ->
    manager.addAxiom(outont, ax)
  }
}
println "Processing cl"
ont2 = manager.loadOntologyFromOntologyDocument(IRI.create("http://purl.obolibrary.org/obo/cl-basic.owl"))
reasoner = f1.createReasoner(ont2, config)
generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator(), new InferredClassAssertionAxiomGenerator(), new InferredEquivalentClassAxiomGenerator(), new InferredSubClassAxiomGenerator()])
generator.fillOntology(fac, outont)
ont2.getTBoxAxioms(Imports.INCLUDED).each { ax ->
  if (! (ax.isOfType(AxiomType.DISJOINT_CLASSES))) {
    manager.addAxiom(outont, ax)
  }
}
ont2.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationAssertionAxioms(cl, ont2).each { ax ->
    manager.addAxiom(outont, ax)
  }
}
println "Processing nbo"
ont2 = manager.loadOntologyFromOntologyDocument(IRI.create("http://purl.obolibrary.org/obo/nbo.owl"))
reasoner = f1.createReasoner(ont2, config)
generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator(), new InferredClassAssertionAxiomGenerator(), new InferredEquivalentClassAxiomGenerator(), new InferredSubClassAxiomGenerator()])
generator.fillOntology(fac, outont)
ont2.getTBoxAxioms(Imports.INCLUDED).each { ax ->
  if (! (ax.isOfType(AxiomType.DISJOINT_CLASSES))) {
    manager.addAxiom(outont, ax)
  }
}
ont2.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationAssertionAxioms(cl, ont2).each { ax ->
    manager.addAxiom(outont, ax)
  }
}
// println "Processing pr"
// ont2 = manager.loadOntologyFromOntologyDocument(IRI.create("http://purl.obolibrary.org/obo/pr.owl"))
// reasoner = f1.createReasoner(ont2, config)
// generator = new InferredOntologyGenerator(reasoner, [new InferredSubClassAxiomGenerator(), new InferredClassAssertionAxiomGenerator(), new InferredEquivalentClassAxiomGenerator(), new InferredSubClassAxiomGenerator()])
// generator.fillOntology(fac, outont)
// ont2.getTBoxAxioms(Imports.INCLUDED).each { ax ->
//   if (! (ax.isOfType(AxiomType.DISJOINT_CLASSES))) {
//     manager.addAxiom(outont, ax)
//   }
// }
// ont2.getClassesInSignature(true).each { cl ->
//   EntitySearcher.getAnnotationAssertionAxioms(cl, ont2).each { ax ->
//     manager.addAxiom(outont, ax)
//   }
// }




println "Building ontology..."

def map = [:]

String formatClassNames(String s) {
  s=s.replace("<http://purl.obolibrary.org/obo/","")
  s=s.replace(">","")
  s=s.replace("_",":")
  s
}
def id2class = [:] // maps a name to an OWLClass
ont.getClassesInSignature(true).each {
  def aa = it.toString()
  aa = formatClassNames(aa)
  if (id2class[aa] != null) {
  } else {
    id2class[aa] = it
  }
}
def id2name = [:]
ont.getClassesInSignature(true).each { cl ->
  EntitySearcher.getAnnotationObjects(cl, ont, fac.getRDFSLabel()).each { lab ->
    id2name[cl] = lab.getValue().asLiteral()
  }
}
def addAnno = {resource, prop, cont ->
  //  OWLAnnotation anno = fac.getOWLAnnotation(fac.getOWLAnnotationProperty(prop.getIRI()), fac.getOWLLiteral(cont))
  def axiom = fac.getOWLAnnotationAssertionAxiom(fac.getOWLAnnotationProperty(prop.getIRI()), resource.getIRI(), cont)
  manager.addAxiom(outont,axiom)
}

def R = { String s ->
  if (s == "part-of") {
    fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/BFO_0000050"))
  } else if (s == "has-part") {
    fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/BFO_0000051"))
  } else {
    fac.getOWLObjectProperty(IRI.create("http://aber-owl.net/#"+s))
  }
}

def C = { String s ->
  fac.getOWLClass(IRI.create(onturi+s))
}

def and = { cl1, cl2 ->
  fac.getOWLObjectIntersectionOf(cl1,cl2)
}
def some = { r, cl ->
  fac.getOWLObjectSomeValuesFrom(r,cl)
}
def equiv = { cl1, cl2 ->
  fac.getOWLEquivalentClassesAxiom(cl1, cl2)
}
def subclass = { cl1, cl2 ->
  fac.getOWLSubClassOfAxiom(cl1, cl2)
}

ont.getClassesInSignature(true).each { cl ->
  if (cl.toString().indexOf("MP_")>-1 || cl.toString().indexOf("HP_")>-1) {
    def q = []
    def e = []
    def e2 = []
    def po = []
    def ihp = []
    def modifier = []
    def occursin = []
    def haspart = []
    def during = []
    def hasquality = []
    def centralparticipant = []
    def resultsfrom = []
    EntitySearcher.getEquivalentClasses(cl, ont).each { cExpr -> // OWL Class Expression
      if (! cExpr.isClassExpressionLiteral()) {
	if (cExpr.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM) {
	  def c = cExpr as OWLQuantifiedRestriction
	  if (c.getProperty()?.toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>") {
	    c = c.getFiller().asConjunctSet()
	    c.each { conj ->
	      if (conj.isClassExpressionLiteral()) {
		q << conj
	      } else if (conj.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM) {
		conj = conj as OWLQuantifiedRestriction
		if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0002573>") { // modifier
		  modifier << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0000052>") { // inheres-in
		  e << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0002314>") { // inheres in part of (make part-of some E)
		  ihp << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/RO_0002503>") { // towards
		  e2 << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#has_quality>") { // has-quality (make quality of Q)
		  hasquality << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#exists_during>") { // exists-during (modified/intersect of E2)
		  during << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000051>") { // has-part: treat as intersection ( :( )
		  haspart << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/BFO_0000050>") { // part-of (E and part-of some X)
		  po << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#has_central_participant>") { // has-central-participant (?)
		  centralparticipant << conj.getFiller()
		} else if (conj.getProperty().toString() == "<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#results_from>") { // has-central-participant (?)
		  resultsfrom << conj.getFiller()
		} else if (conj.getProperty().toString() in ["<http://purl.obolibrary.org/obo/BFO_0000066>","<http://purl.obolibrary.org/obo/mp/mp-equivalent-axioms-subq#occurs_in>"]) { // occurs-in: make modifier to E (E occurs in ...)
		  occursin << conj.getFiller()
		} else {
		  println "Ignoring $cl: "+conj.getProperty()
		}
	      }
	    }
	  }
	}
      }
    }
    // def q = []
    // def e = []
    // def e2 = []
    // def po = []
    // def ihp = []
    // def modifier = []
    // def occursin = []
    // def haspart = []
    // def during = []
    // def hasquality = []
    // def centralparticipant = []
    Expando exp = new Expando()
    exp.cl = cl
    exp.e = e
    exp.e2 = e2
    exp.q = q
    exp.ihp = ihp
    exp.mod = modifier
    exp.occ = occursin
    exp.hp = haspart
    exp.during = during
    exp.hasquality = hasquality
    exp.centralparticipant = centralparticipant
    exp.resultsfrom = resultsfrom
    map[cl] = exp
    fout.println(exp)
  }
}
