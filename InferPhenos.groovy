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

def posReg = [:].withDefault {key -> return new HashSet<String>()}
def negReg = [:].withDefault {key -> return new HashSet<String>()}

// Positive Regulation
def pr = fac.getOWLObjectProperty(
    IRI.create("http://purl.obolibrary.org/obo/RO_0002213"))
// Negative Regulation
def nr = fac.getOWLObjectProperty(
    IRI.create("http://purl.obolibrary.org/obo/RO_0002212"))


def getLabel = { term_id ->
    IRI iri = IRI.create("http://purl.obolibrary.org/obo/$term_id")
    OWLClass cl = dataFactory.getOWLClass(iri)
    for(OWLAnnotation a : EntitySearcher.getAnnotations(cl, ont, dataFactory.getRDFSLabel())) {
        OWLAnnotationValue value = a.getValue();
        if(value instanceof OWLLiteral) {
            return ((OWLLiteral) value).getLiteral();
        }
    }
    return "";
}

GParsPool.withPool {
    ont.getClassesInSignature(true).eachParallel { cl ->
        def cls = cl.toString()
        cls = cls.substring(32, cls.length() - 1)
        def c = fac.getOWLObjectSomeValuesFrom(pr, cl)

        reasoner.getSubClasses(c, false).getFlattened().each { sub ->
            def s = sub.toString()
            if (s.startsWith("<http://purl.obolibrary.org/obo/GO_")) {
                s = s.substring(32, s.length() - 1)
                posReg[s].add(cls)
            }
        }
        c = fac.getOWLObjectSomeValuesFrom(nr, cl)
        reasoner.getSubClasses(c, false).getFlattened().each { sub ->
            def s = sub.toString()
            if (s.startsWith("<http://purl.obolibrary.org/obo/GO_")) {
                s = s.substring(32, s.length() - 1)
                negReg[s].add(cls)
            }
        }
    }
}

def incPheno = [:].withDefault { new HashSet<String>() }
def decPheno = [:].withDefault { new HashSet<String>() }
def abnPheno = [:].withDefault { new HashSet<String>() }

new File("data/pheno2go.txt").splitEachLine("  ") { items ->
    def pheno = items[0]
    def go = items[1]
    if (items[2] == "1") {          // increase
        incPheno[go].add(pheno)
    } else if (items[2] == "-1") {  // decrease
        decPheno[go].add(pheno)
    } else {                        // abnormal
        abnPheno[go].add(pheno)
    }
}

def expCodes = ["EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "TAS", "IC"]
def annotations = [:].withDefault{ new HashSet() }
new File("data/gene_association.goa_human").splitEachLine("\t") { items ->
    if (items.size() > 1) {
        def mgi = items[2]
        if (!(items[6] in expCodes) || items[3] == "NOT") {
            return
        }
        if (items[4] != null && items[4].startsWith("GO:")) {
            def go = items[4].replaceAll(":", "_")
            annotations[mgi].add(go)
        }
    }
}


def out = new PrintWriter(new BufferedWriter(new FileWriter("data/predictions_human.txt")))

GParsPool.withPool {
    annotations.eachParallel { mgi, gos ->
        gos.each { go ->
            if (go in abnPheno) {
                abnPheno[go].each { pheno ->
                    out.println("$mgi\t$go\t$pheno\t0")
                }
            }

            if (go in posReg) {
                posReg[go].each { g_id ->
                    if (g_id in decPheno) {
                        decPheno[g_id].each { pheno ->
                            out.println("$mgi\t$go\t$pheno\t-1")
                        }
                    }
                    if (g_id in incPheno) { // inconsistent
                        incPheno[g_id].each { pheno ->
                            out.println("$mgi\t$go\t$pheno\t2")
                        }
                    }
                }
            }
            if (go in negReg) {
                negReg[go].each { g_id ->
                    if (g_id in decPheno) {  // inconsistent
                        decPheno[g_id].each { pheno ->
                            out.println("$mgi\t$go\t$pheno\t-2")
                        }
                    }
                    if (g_id in incPheno) {
                        incPheno[g_id].each { pheno ->
                            out.println("$mgi\t$go\t$pheno\t1")
                        }
                    }

                }
            }
        }
    }
}
out.flush()
out.close()

