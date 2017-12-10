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
def mgiAnnots = [:].withDefault {new HashSet<String>()}

new File("data/diseases_to_genes_to_phenotypes.txt").eachLine { line ->
  if (line.startsWith("#")) return;
  def items = line.split("\t")
  def gene = items[1]
  def hp = items[3].replaceAll(":", "_")
  if (hp in phenos) {
    geneAnnots[gene].add(hp)
  }
}

new File("data/MGI_GenePheno.rpt").splitEachLine("\t") { items ->
  pheno = items[4].replaceAll(":", "_")
  if (pheno in phenos) {
    def mgis = items[6].split(",")
    mgis.each { mgi ->
	    mgiAnnots[mgi].add(pheno)
    }
  }
}

def mp2hp = [:]
phenomenet.getClassesInSignature().each {
    cl ->
    def name = getName(cl);
    if (name.startsWith("MP_")) {
	def eClasses = phenomeReasoner.getEquivalentClasses(cl).getEntities()
	eClasses.each {
	    ecl ->
	    eName = getName(ecl)
	    if (eName.startsWith('HP_')) {
		mp2hp[name] = eName;
	    }
	}
    }
}


// def homos = [:]
// new File("data/hom_mouse.tab").splitEachLine("\t") { items ->
//   def homo_id = items[0]
//   def mgi = items[5]
//   homos[homo_id] = mgi
// }

// def omims = new HashSet<String>();
// def mgis = new HashSet<String>();
// new File("data/mgi_omim.tab").eachLine { line ->
//   if (line.startsWith("#")) return;
//   def items = line.split("\t")
//   omims.add(items[0])
//   // def homo_id = items[2]
//   // if (homo_id in homos) {
//   mgis.add(items[7])
//   // }
// }

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

// out = new PrintWriter(new BufferedWriter(new FileWriter("data/mgi_without_phenos.tab")))
def annotMgis = mgiAnnots.keySet()
def annotGenes = geneAnnots.keySet()
// mgis.each { mgi ->
//   if (!(mgi in annotMgis)) {
//     out.println(mgi)
//   }
// }
// out.close()

// Add all superclasses to the annotations
// annotMgis.each { mgi ->
//   mgiAnnots[mgi].collect().each { pheno ->
//     anchestors = new HashSet<String>()
//     getAnchestors(phenomeReasoner, pheno).each { cl ->
//         def name = getName(cl)
//         if (name.startsWith("MP") || name.startsWith("HP")) {
//             anchestors.add(name)
//         }
//     }
//     mgiAnnots[mgi].addAll(anchestors)
//   }
// }

// Remove inconsistent predictions
removed = 0
new File("data/predictions_incon.txt").splitEachLine("\t") { items ->
    def pheno = items[2]
    def go = items[1]
    def goLabel = getLabel(go)
    if (pheno in phenos) {
	def mgi = items[0]
	if (mgi in annotMgis) {
	    children = new HashSet<String>()
	    children.add(pheno)
	    getChildren(phenomeReasoner, pheno).each { cl ->
		def name = getName(cl)
		if (name.startsWith("MP") || name.startsWith("HP")) {
		    children.add(name)
		}
	    }
	    children.each {child ->
		if (child in mgiAnnots[mgi]) {
		    label = getLabel(child)
		    mgiAnnots[mgi].remove(child)
		    println("$mgi\t$go\t$goLabel\t$child\t$label")
		    removed += 1
		}
	    }
	}
    }
}
println("Removed: $removed")


// Remove inconsistent predictions human
removed = 0
new File("data/predictions_human_incon.txt").splitEachLine("\t") { items ->
    def pheno = items[2]
    def go = items[1]
    def goLabel = getLabel(go)
    if (pheno in phenos) {
	def gene = items[0]
	if (gene in annotGenes) {
	    children = new HashSet<String>()
	    children.add(pheno)
	    getChildren(phenomeReasoner, pheno).each { cl ->
		def name = getName(cl)
		if (name.startsWith("MP") || name.startsWith("HP")) {
		    children.add(name)
		}
	    }
	    if (pheno in mp2hp) {
		def hp = mp2hp[pheno]
		children.add(hp)
		getChildren(phenomeReasoner, hp).each { cl ->
		    def name = getName(cl)
		    if (name.startsWith("MP") || name.startsWith("HP")) {
			children.add(name)
		    }
		}
	    }
	    
	    children.each {child ->
		if (child in geneAnnots[gene]) {
		    label = getLabel(child)
		    geneAnnots[gene].remove(child)
		    println("$gene\t$go\t$goLabel\t$child\t$label")
		    removed += 1
		}
	    }
	}
    }
}
println("Removed: $removed")

// Remove general terms and leave only specific

// mgiAnnots.keySet().each { mgi ->
//   def annots = mgiAnnots[mgi].collect()
//   annots.each { pheno ->
//     getAnchestors(phenomeReasoner, pheno).each { anch ->
//       anch = getName(anch)
//       if (anch in mgiAnnots[mgi]) {
//         mgiAnnots[mgi].remove(anch)
//       }
//     }
//   }
// }

// out = new PrintWriter(new BufferedWriter(new FileWriter("data/mgi_annotations_with_removed.tab")))
// mgiAnnots.each { mgi, annots ->
//   if (mgi in mgis && annots.size() > 0) {
//     out.print(mgi)
//     annots.each { pheno ->
//       out.print("\t" + pheno)
//     }
//     out.println()
//   }
// }
// out.close()


// Add predicted annotations
// mgiAnnots = [:].withDefault {new HashSet<String>()}

// new File("data/predictions_filtered.txt").splitEachLine("\t") { items ->
//   pheno = items[2]
//   if (pheno in phenos) {
//     def mgi = items[0]
//     if (mgi in mgis) {
//       mgiAnnots[mgi].add(pheno)
//     }
//   }
// }

// Remove general terms and leave only specific

// mgiAnnots.keySet().each { mgi ->
//   def annots = mgiAnnots[mgi].collect()
//   annots.each { pheno ->
//     getAnchestors(phenomeReasoner, pheno).each { anch ->
//       anch = getName(anch)
//       if (anch in mgiAnnots[mgi]) {
//         mgiAnnots[mgi].remove(anch)
//       }
//     }
//   }
// }

// out = new PrintWriter(new BufferedWriter(new FileWriter("data/mgi_annotations_only_pred.tab")))
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
