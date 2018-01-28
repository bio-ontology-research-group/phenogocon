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

// OWLOntologyManager manager = OWLManager.createOWLOntologyManager()
// OWLOntology phenomenet = manager.loadOntologyFromOntologyDocument(
//     new File("data/a.owl"))

// OWLDataFactory fac = manager.getOWLDataFactory()
// ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
// OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
// OWLDataFactory dataFactory = manager.getOWLDataFactory()
// ElkReasonerFactory reasonerFactory = new ElkReasonerFactory()
// OWLReasoner phenomeReasoner = reasonerFactory.createReasoner(
//     phenomenet, config)

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

new File("data/phenos.tab").eachLine { line ->
    def pheno = line.trim()
    phenos.add(pheno)
}


def omimAnnots = [:].withDefault {new HashSet<String>()}
def geneAnnots = [:].withDefault {new HashSet<String>()}
def mgiAnnots = [:].withDefault {new HashSet<String>()}

def omims = new HashSet<String>();
def genes = new HashSet<String>();

new File("data/diseases_to_genes.txt").eachLine { line ->
    if (line.startsWith("#")) return;
    if (!line.startsWith("OMIM")) return;
    def items = line.split("\t")
    if (items.size() != 3) return;
    omims.add(items[0])
    genes.add(items[2])
}

// new File("data/human_omim.tab").eachLine { line ->
//   if (line.startsWith("#")) return;
//     def items = line.split("\t")
//     for (def omim: items[2].split("\\|")) { 
// 	if (omim != "") omims.add(omim)
//     }
//     genes.add(items[6])
// }

new File("data/phenotype_annotation.tab").splitEachLine("\t") { items ->
    if (items[0] != "OMIM") return;
    def omim = items[0] + ":" + items[1];
    pheno = items[4].replaceAll(":", "_")
    if (pheno in phenos) {
	omimAnnots[omim].add(pheno)
    }
}


// new File("data/genes_to_phenotype.txt").eachLine { line ->
//     if (line.startsWith("#")) return;
//     def items = line.split("\t")
//     def gene = items[1]
//     def hp = items[3].replaceAll(":", "_")
//     if (hp in phenos) {
// 	geneAnnots[gene].add(hp)
//     }
// }

new File("data/MGI_GenePheno.rpt").splitEachLine("\t") { items ->
    pheno = items[4].replaceAll(":", "_")
    if (pheno in phenos) {
	def mgis = items[6].split("\\|")
	mgis.each { mgi ->
	    mgiAnnots[mgi].add(pheno)
	}
    }
}

def homo2mgi = [:]

new File("data/HOM_MouseHumanSequence.rpt").eachLine { line ->
    def items = line.split("\t", -1)
    if (items[2] == "10090") {
	homo2mgi[items[0]] = items[5]
    } else if(items[2] == "9606") {
	gene = items[3]
	mgi = homo2mgi[items[0]]
	if (mgiAnnots.containsKey(mgi)) {
	    geneAnnots[gene].addAll(mgiAnnots[mgi])
	}
    }
}


// Add predicted annotations
geneAnnots = [:].withDefault {new HashSet<String>()}

new File("data/predictions_human_filtered.txt").splitEachLine("\t") { items ->
  pheno = items[2]
  if (pheno in phenos) {
    def gene = items[0]
    geneAnnots[gene].add(pheno)
  }
}

// new File("data/predictions_deep_human_filtered.txt").splitEachLine("\t") { items ->
//   pheno = items[2]
//   if (pheno in phenos) {
//     def gene = items[0]
//     geneAnnots[gene].add(pheno)
//   }
// }

// Remove general terms and leave only specific

// geneAnnots.keySet().each { gene ->
//   def annots = geneAnnots[gene].collect()
//   annots.each { pheno ->
//     getAnchestors(phenomeReasoner, pheno).each { anch ->
//       anch = getName(anch)
//       if (anch in geneAnnots[gene]) {
//         geneAnnots[gene].remove(anch)
//       }
//     }
//   }
// }


out = new PrintWriter(new BufferedWriter(new FileWriter("data/human_mp_annotations_only_pred.tab")))
geneAnnots.each { gene, annot ->
    if (gene in genes) {
	out.print(gene)
	annot.each { pheno ->
	    out.print("\t" + pheno)
	}
	out.println()
    }
}
out.close()

// out = new PrintWriter(new BufferedWriter(new FileWriter("data/omim_human_annotations.tab")))
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
