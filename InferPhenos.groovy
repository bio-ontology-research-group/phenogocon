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

OWLOntologyManager manager = OWLManager.createOWLOntologyManager()
OWLOntology ont = manager.loadOntologyFromOntologyDocument(new File("go-basic.obo"))
OWLDataFactory fac = manager.getOWLDataFactory()
ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
ElkReasonerFactory f1 = new ElkReasonerFactory()
OWLReasoner reasoner = f1.createReasoner(ont,config)
reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY)

def regmap = [:].withDefault { [:].withDefault { new TreeSet() } }

def fout = new PrintWriter(new BufferedWriter(new FileWriter("inferred-phenos.txt")))

def pr = fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/RO_0002213"))
def nr = fac.getOWLObjectProperty(IRI.create("http://purl.obolibrary.org/obo/RO_0002212"))
ont.getClassesInSignature(true).each { cl ->
  def clstring = cl.toString().replaceAll("<http://purl.obolibrary.org/obo/GO_","GO:").replaceAll(">","")
  def c = fac.getOWLObjectSomeValuesFrom(pr, cl)
  reasoner.getSubClasses(c, false).getFlattened().each { sub ->
    def subs = sub.toString().replaceAll("<http://purl.obolibrary.org/obo/GO_","GO:").replaceAll(">","")
    regmap[subs]["up"].add(clstring)
  }
  c = fac.getOWLObjectSomeValuesFrom(nr, cl)
  reasoner.getSubClasses(c, false).getFlattened().each { sub ->
    def subs = sub.toString().replaceAll("<http://purl.obolibrary.org/obo/GO_","GO:").replaceAll(">","")
    regmap[subs]["down"].add(clstring)
  }
}


def map = [:].withDefault { [:] }

def down = ["http://purl.obolibrary.org/obo/PATO_0000462", "http://purl.obolibrary.org/obo/PATO_0000381", "http://purl.obolibrary.org/obo/PATO_0000911", "http://purl.obolibrary.org/obo/PATO_0000297", "http://purl.obolibrary.org/obo/PATO_0001511", "http://purl.obolibrary.org/obo/PATO_0001507"]
def up = ["http://purl.obolibrary.org/obo/PATO_0000912"]

new File("pheno2go.txt").splitEachLine("\t") { line ->
  def mp = line[0]
  def go = line[1].replaceAll("http://purl.obolibrary.org/obo/GO_","GO:")
  if (line[2] in down) { // decreased
    map[go]["down"] = mp
  }
  if (line[2] in up ) { // increased
    map[go]["up"] = mp
  }
  if (line[2] == "http://purl.obolibrary.org/obo/PATO_0000001") { // abnormal
    map[go]["abnormal"] = mp
  }
}


def mgi2go = [:].withDefault{ new TreeSet() }
new File("gene_association.mgi").splitEachLine("\t") { line ->
  if (line.size()>1) {
    def mgi = line[1]
    def go = line[4]
    mgi2go[mgi].add(go)
  }
}
mgi2go.each { mgi, gos ->
  gos.each { go ->
    if (map[go]["abnormal"]) {
      fout.println("$mgi\t$go\t"+map[go]["abnormal"])
    }
    if (regmap[go]["up"]) {
      def go2 = regmap[go]["up"] // go upregulates go2
      go2.each { g2 ->
	if (map[g2]["down"]) { // find the "decreased go2 phenotype
	  fout.println("$mgi\t$go\t"+map[g2]["down"]+"\tdown")
	}
      }
    }
    if (regmap[go]["down"]) {
      def go2 = regmap[go]["down"]
      go2.each { g2 ->
	if (map[g2]["up"]) {
	  fout.println("$mgi\t$go\t"+map[g2]["up"]+"\tup")
	}
      }
    }
  }
}
fout.flush()
fout.close()

