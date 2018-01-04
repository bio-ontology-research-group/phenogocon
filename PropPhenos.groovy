@Grapes([
    @Grab(group="org.semanticweb.elk", module="elk-owlapi", version="0.4.2"),
    @Grab(group="net.sourceforge.owlapi", module="owlapi-api", version="4.1.0"),
    @Grab(group="net.sourceforge.owlapi", module="owlapi-apibinding", version="4.1.0"),
    @Grab(group="net.sourceforge.owlapi", module="owlapi-impl", version="4.1.0"),
    @Grab(group="net.sourceforge.owlapi", module="owlapi-parsers", version="4.1.0"),
    @Grab(group="org.codehaus.gpars", module="gpars", version="1.1.0"),
    @GrabConfig(systemClassLoader=true)
])

import org.semanticweb.owlapi.model.parameters.*;
import org.semanticweb.elk.owlapi.ElkReasonerFactory;
import org.semanticweb.elk.owlapi.ElkReasonerConfiguration;
import org.semanticweb.elk.reasoner.config.*;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.reasoner.*;
import org.semanticweb.owlapi.reasoner.structural.StructuralReasoner
import org.semanticweb.owlapi.vocab.OWLRDFVocabulary;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.io.*;
import org.semanticweb.owlapi.owllink.*;
import org.semanticweb.owlapi.util.*;
import org.semanticweb.owlapi.search.*;
import org.semanticweb.owlapi.manchestersyntax.renderer.*;
import org.semanticweb.owlapi.reasoner.structural.*;

import groovyx.gpars.GParsPool;

OWLOntologyManager manager = OWLManager.createOWLOntologyManager()
OWLOntology ont = manager.loadOntologyFromOntologyDocument(
    new File("data/go.owl"))
OWLDataFactory dataFactory = manager.getOWLDataFactory()
OWLDataFactory fac = manager.getOWLDataFactory()
ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
ElkReasonerFactory f1 = new ElkReasonerFactory()
OWLReasoner reasoner = f1.createReasoner(ont, config)
reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY)

def getChildren = { term_id ->
    IRI iri = IRI.create("http://purl.obolibrary.org/obo/$term_id")
    OWLClass cl = dataFactory.getOWLClass(iri)
    def res = reasoner.getSubClasses(cl, false).getFlattened()
    return res
}

def getName = { cl ->
  def iri = cl.toString()
  def name = iri
  if (iri.startsWith("<http://purl.obolibrary.org/obo/")) {
    name = iri.substring(32, iri.length() - 1)
  } else if (iri.startsWith("<http://aber-owl.net/")) {
    name = iri.substring(21, iri.length() - 1)
  }
  return name
}

def out = new PrintWriter(new BufferedWriter(new FileWriter("data/rules_prop.txt")))

new File("data/rules.txt").splitEachLine("\t") { items ->
    def go_id = items[0]
    def pred = items[1] + "\t" + items[2];
    out.println("$go_id\t$pred");
    getChildren(go_id).each { term_id ->
	term_id = getName(term_id)
	out.println("$term_id\t$pred")
    }
}

out.close();
