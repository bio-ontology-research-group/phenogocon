@Grapes([
    @Grab(group='org.semanticweb.elk', module='elk-owlapi', version='0.4.2'),
    @Grab(group='net.sourceforge.owlapi', module='owlapi-api', version='4.1.0'),
    @Grab(group='net.sourceforge.owlapi', module='owlapi-apibinding', version='4.1.0'),
    @Grab(group='net.sourceforge.owlapi', module='owlapi-impl', version='4.1.0'),
    @Grab(group='net.sourceforge.owlapi', module='owlapi-parsers', version='4.1.0'),
    @Grab(group='org.codehaus.gpars', module='gpars', version='1.1.0'),
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
OWLOntology phenomenet = manager.loadOntologyFromOntologyDocument(
    new File("data/a.owl"))

OWLDataFactory fac = manager.getOWLDataFactory()
ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
OWLDataFactory dataFactory = manager.getOWLDataFactory()
ElkReasonerFactory reasonerFactory = new ElkReasonerFactory()
OWLReasoner phenomeReasoner = reasonerFactory.createReasoner(
    phenomenet, config)

def getLabel = { term_id ->
    IRI iri = IRI.create("http://purl.obolibrary.org/obo/$term_id")
    OWLClass cl = dataFactory.getOWLClass(iri)
    for(OWLAnnotation a : EntitySearcher.getAnnotations(cl, phenomenet, dataFactory.getRDFSLabel())) {
        OWLAnnotationValue value = a.getValue();
        if(value instanceof OWLLiteral) {
            return ((OWLLiteral) value).getLiteral();
        }
    }
    return "";
}
def getAnchestors = { reasoner, term_id ->
    IRI iri = IRI.create("http://purl.obolibrary.org/obo/$term_id")
    OWLClass cl = dataFactory.getOWLClass(iri)
    def res = reasoner.getSuperClasses(cl, false).getFlattened()
    return res
}

def getChildren = { reasoner, term_id ->
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

def phenos = new HashSet<String>();

GParsPool.withPool {
  phenomenet.getClassesInSignature(true).eachParallel { cl ->
    def name = getName(cl)
    if (name.startsWith("MP") || name.startsWith("HP")) {
      phenos.add(name)
    }
  }
}

def geneAnnots = [:].withDefault {new HashSet<String>()}

new File("data/genes_to_phenotype.txt").eachLine { line ->
    if (line.startsWith("#")) return;
    def items = line.split("\t")
    def gene = items[1]
    def hp = items[3].replaceAll(":", "_")
    if (hp in phenos) {
	geneAnnots[gene].add(hp)
    }
}

// Add predicted annotations
predAnnots = [:].withDefault {new HashSet<String>()}

new File("data/predictions_human_filtered.txt").splitEachLine("\t") { items ->
  pheno = items[2]
  if (pheno in phenos) {
    def gene = items[0]
    predAnnots[gene].add(pheno)
  }
}

// Remove general terms and leave only specific

predAnnots.keySet().each { gene ->
  def annots = predAnnots[gene].collect()
  annots.each { pheno ->
    getAnchestors(phenomeReasoner, pheno).each { anch ->
      anch = getName(anch)
      if (anch in predAnnots[gene]) {
        predAnnots[gene].remove(anch)
      }
    }
  }
}

def out = new PrintWriter(new BufferedWriter(new FileWriter("data/human_pred_annotations.tab")))
geneAnnots.each { gene, annots ->
  if (gene in predAnnots) {
    out.print(gene)
    annots.each { pheno ->
      out.print("\t" + pheno)
    }
    out.println()
    out.print(gene)
    predAnnots[gene].each { pheno ->
      out.print("\t" + pheno)
    }
    out.println()
  }
}
out.close()


// out = new PrintWriter(new BufferedWriter(new FileWriter("data/human_annotations_only_pred.tab")))
// geneAnnots.each { gene, annot ->
//     out.print(gene)
//     annot.each { pheno ->
//       out.print("\t" + pheno)
//     }
//     out.println()
// }
// out.close()
