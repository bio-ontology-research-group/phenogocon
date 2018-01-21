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

def mgiAnnots = [:].withDefault {new HashSet<String>()}

new File("data/MGI_GenePheno.rpt").splitEachLine("\t") { items ->
    pheno = items[4].replaceAll(":", "_")
    if (pheno in phenos) {
	def mgis = items[6].split(",")
	mgis.each { mgi ->
	    mgiAnnots[mgi].add(pheno)
	}
    }
}

// def omims = new HashSet<String>();
// def mgis = new HashSet<String>();
// new File("data/mgi_omim.tab").eachLine { line ->
//   if (line.startsWith("#")) return;
//   def items = line.split("\t")
//   omims.add(items[0])
//   mgis.add(items[7])
// }


// Add predicted annotations
predAnnots = [:].withDefault {new HashSet<String>()}

new File("data/predictions_filtered.txt").splitEachLine("\t") { items ->
  pheno = items[2]
  if (pheno in phenos) {
    def gene = items[0]
   // if (gene in mgis) {	
      predAnnots[gene].add(pheno)
   // }
  }
}

// Remove general terms and leave only specific

predAnnots.keySet().each { mgi ->
  def annots = predAnnots[mgi].collect()
  annots.each { pheno ->
    getAnchestors(phenomeReasoner, pheno).each { anch ->
      anch = getName(anch)
      if (anch in predAnnots[mgi]) {
        predAnnots[mgi].remove(anch)
      }
    }
  }
}

def out = new PrintWriter(new BufferedWriter(new FileWriter("data/mgi_pred_annotations.tab")))
mgiAnnots.each { mgi, annots ->
  if (mgi in predAnnots) {
    out.print(mgi)
    annots.each { pheno ->
      out.print("\t" + pheno)
    }
    out.println()
    out.print(mgi)
    predAnnots[mgi].each { pheno ->
      out.print("\t" + pheno)
    }
    out.println()
  }
}
out.close()


// def out = new PrintWriter(new BufferedWriter(new FileWriter("data/mgi_annotations.tab")))
// mgiAnnots.each { mgi, annots ->
//   if (mgi in mgis) {
//     out.print(mgi)
//     annots.each { pheno ->
//       out.print("\t" + pheno)
//     }
//     out.println()
//   }
// }
// out.close()


// out = new PrintWriter(new BufferedWriter(new FileWriter("data/omim_annotations.tab")))
// omimAnnots.each { omim, annots ->
//   if (omim in omims) {
//     out.print(omim)
//     annots.each { pheno ->
//       out.print("\t" + pheno)
//     }
//     out.println()
//   }
// }
// out.close()
