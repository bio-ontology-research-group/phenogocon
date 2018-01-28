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
// OWLOntology go = manager.loadOntologyFromOntologyDocument(
//     new File("data/go.owl"))
// OWLOntology phenomenet = manager.loadOntologyFromOntologyDocument(
//     new File("data/a.owl"))

// OWLDataFactory fac = manager.getOWLDataFactory()
// ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
// OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
// OWLDataFactory dataFactory = manager.getOWLDataFactory()
// ElkReasonerFactory reasonerFactory = new ElkReasonerFactory()
// OWLReasoner goReasoner = reasonerFactory.createReasoner(go, config)
// OWLReasoner phenomeReasoner = reasonerFactory.createReasoner(
//     phenomenet, config)
// def shortFormProvider = new SimpleShortFormProvider()

// def getAnchestors = { reasoner, term_id ->
//     IRI iri = IRI.create("http://purl.obolibrary.org/obo/$term_id")
//     OWLClass cl = dataFactory.getOWLClass(iri)
//     def res = reasoner.getSuperClasses(cl, false).getFlattened()
//     return res
// }

// def getChildren = { reasoner, term_id ->
//     IRI iri = IRI.create("http://purl.obolibrary.org/obo/$term_id")
//     OWLClass cl = dataFactory.getOWLClass(iri)
//     def res = reasoner.getSubClasses(cl, false).getFlattened()
//     return res
// }


// def getName = { cl ->
//   return shortFormProvider.getShortForm(cl)
// }

// def mp2hp = [:]
// phenomenet.getClassesInSignature().each {
//     cl ->
//     def name = getName(cl);
//     if (name.startsWith("MP_")) {
// 	def eClasses = phenomeReasoner.getEquivalentClasses(cl).getEntities()
// 	eClasses.each {
// 	    ecl ->
// 	    eName = getName(ecl)
// 	    if (eName.startsWith('HP_')) {
// 		mp2hp[name] = eName;
// 	    }
// 	}
//     }
// }

annotations = [:].withDefault { new HashSet<String>() }
predictions = [:].withDefault { [:].withDefault { new HashSet<String>() } }

def qual = [:].withDefault { [:] }

new File("data/predictions_filtered.txt").splitEachLine("\t") { items ->
    def pheno = items[2].replaceAll(":", "_")
    def children = new HashSet<String>()
    children.add(pheno)
    // getChildren(phenomeReasoner, pheno).each { cl ->
    //     def name = getName(cl)
    //     if (name.startsWith("MP") || name.startsWith("HP")) {
    //         children.add(name)
    //     }
    // }
    gene = items[0]
    annot = items[1]
    predictions[gene][annot].addAll(children)
    qual[annot][pheno] = items[3]
}

new File("data/MGI_GenePheno.rpt").splitEachLine("\t") { items ->
    pheno = items[4].replaceAll(":", "_")
    anchestors = new HashSet<String>()
    anchestors.add(pheno)
    // getAnchestors(phenomeReasoner, pheno).each { cl ->
    //     def name = getName(cl)
    //     if (name.startsWith("MP") || name.startsWith("HP")) {
    //         anchestors.add(name)
    //     }
    // }

    mgis = items[6].split(",")
    mgis.each { mgi ->
	if (mgi in predictions) {
	    predictions[mgi].each { go_id, phenos ->
		if (anchestors.intersect(phenos).size() > 0) {
		    def ql = qual[go_id][pheno]
		    println("$mgi\t$go_id\t$pheno\t$ql");
		}
	    }
	}
        annotations[mgi].addAll(anchestors)
    }
}

new File("data/genes_to_phenotype.txt").eachLine { line ->
    if (line.startsWith("#")) return;
    def items = line.split("\t")
    def gene = items[1]
    def hp = items[3].replaceAll(":", "_")
    anchestors = new HashSet<String>()
    anchestors.add(hp)
    // getAnchestors(phenomeReasoner, hp).each { cl ->
    //     def name = getName(cl)
    //     if (name.startsWith("MP") || name.startsWith("HP")) {
    //         anchestors.add(name)
    //     }
    // }

    if (gene in predictions) {
	predictions[gene].each { go_id, phenos ->
	    if (anchestors.intersect(phenos).size() > 0) {
		def ql = qual[go_id][hp]
		println("$gene\t$go_id\t$hp\t$ql");
	    }
	}
    }
    annotations[gene].addAll(anchestors)
    
}
