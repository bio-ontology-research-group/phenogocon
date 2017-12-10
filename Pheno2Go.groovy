@Grapes([
  @Grab(group='org.semanticweb.elk', module='elk-owlapi', version='0.4.2'),
  @Grab(group='net.sourceforge.owlapi', module='owlapi-api', version='4.1.0'),
  @Grab(group='net.sourceforge.owlapi', module='owlapi-apibinding', version='4.1.0'),
  @Grab(group='net.sourceforge.owlapi', module='owlapi-impl', version='4.1.0'),
  @Grab(group='net.sourceforge.owlapi', module='owlapi-parsers', version='4.1.0'),
  @GrabConfig(systemClassLoader=true)
  ])

import org.semanticweb.owlapi.model.parameters.*
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.reasoner.*
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.io.*;
import org.semanticweb.owlapi.owllink.*;
import org.semanticweb.owlapi.util.*;
import org.semanticweb.owlapi.search.*;
import org.semanticweb.elk.owlapi.ElkReasonerFactory;
import org.semanticweb.elk.owlapi.ElkReasonerConfiguration
import org.semanticweb.elk.reasoner.config.*
import java.util.*


def out = new PrintWriter(new BufferedWriter(
  new FileWriter("data/pheno2go.txt")))

OWLOntologyManager manager = OWLManager.createOWLOntologyManager()
OWLOntology ont = manager.loadOntologyFromOntologyDocument(
  new File("data/a.owl"))
OWLDataFactory dataFactory = manager.getOWLDataFactory()
ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
ElkReasonerFactory reasonerFactory = new ElkReasonerFactory()
OWLReasoner reasoner = reasonerFactory.createReasoner(ont, config)

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

def down = [
  "PATO_0000462", // absent
  "PATO_0001997", // decreased amount
  "PATO_0000381", // decreased frequency
  "PATO_0000911", // decreased rate
  "PATO_0000297", // arrested
  "PATO_0001511", // non-functional
  "PATO_0001507", // disrupted
  "PATO_0002304", // decreased process quality
  "PATO_0002018", // decreased magnitude
  "PATO_0001570", // having decreased processual parts
  "PATO_0000708", // decreased threshold
  "PATO_0002058", // decreased area
  "PATO_0001588", // decreased variability of rate
  "PATO_0000499", // decreased duration
  "PATO_0001624", // decreased functionality
  "PATO_0000381", // decreased frequency
  "PATO_0000569", // decreased height
  "PATO_0000574", // decreased length
  "PATO_0001783", // decreased intensity
  "PATO_0000297", // arrested
  "PATO_0000587", // decreased size
  "PATO_0001558", // lacking processual parts
  "PATO_0000592", // decreased thickness
  "PATO_0001562", // decreased mass
  "PATO_0002001", // has fewer parts of type
].toSet()

def up = [
  "PATO_0002304", // increased process quality
  "PATO_0002017", // increased magnitude
  "PATO_0000912", // increased rate
  "PATO_0000706", // increased threshold
  "PATO_0002057", // increased area
  "PATO_0000396", // severe intensity
  "PATO_0000498", // increased duration
  "PATO_0001587", // increased variability of rate
  "PATO_0000380", // increased frequency
  "PATO_0000573", // increased length
  "PATO_0001782", // increased intensity
  "PATO_0000586", // increased size
  "PATO_0000470", // increased amount
  "PATO_0000591", // increased thickness
  "PATO_0001563", // increased mass
].toSet()

def allQual = new HashSet()
def ignored_gos = ["GO_0006954"].toSet()

ont.getClassesInSignature(true).each { cl ->
  clName = getName(cl)
  if (clName.startsWith("MP_") || clName.startsWith("HP_")) {
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
    def qualities = new HashSet()
    EntitySearcher.getEquivalentClasses(cl, ont).each { cExpr ->
      if (!cExpr.isClassExpressionLiteral()) {
        if (cExpr.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM) {
          def c = cExpr as OWLQuantifiedRestriction
          def prop = getName(c.getProperty())
          if (prop == "BFO_0000051") {
            filler = c.getFiller()
            c = c.getFiller().asConjunctSet()
            def hasGO = false;
            def hasUberon = false;
            c.each { conj ->
              def name = getName(conj);
              if (conj.isClassExpressionLiteral() && name.startsWith("GO")) {
                hasGO = true;
              } else if (conj.isClassExpressionLiteral() && name.startsWith("UBER")) {
                hasUberon = true;
              } else if (conj.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM) {
                def cc = conj as OWLQuantifiedRestriction;
                ff = cc.getFiller()
                if (ff.isClassExpressionLiteral() && getName(ff).startsWith("UBER")) {
                  hasUberon = true;
                }
              }
            }
            if (hasGO && hasUberon) {
              return
            }
            if (clName == "MP_0001689") {
              println(c)
            }
            c.each { conj ->
              if (conj.isClassExpressionLiteral()) {
                def conjName = getName(conj);
                if (conjName.startsWith('GO')) {
                  q << conjName;
                } else if (conjName.startsWith('PATO')) {
                  qualities.add(conjName)
                }
              } else if (conj.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM) {
                conj = conj as OWLQuantifiedRestriction
                prop = getName(conj.getProperty())
                filler = conj.getFiller().asConjunctSet()
                if (prop == "RO_0002573") { // modifier
                  modifier << filler
                } else if (prop == "RO_0000052") { // inheres-in
                  e << filler
                } else if (prop == "RO_0002314") { // inheres in part of (make part-of some E)
                  ihp << filler
                } else if (prop in ["RO_0002503", "#towards"]) { // towards
                  e2 << filler
                } else if (prop == "#has_quality" || prop == "#has-quality") { // has-quality (make quality of Q)
                  hasquality << filler
                  filler.each { ce ->
                    if (ce.isClassExpressionLiteral()) {
                      qualities.add(getName(ce))
                    } else if (ce.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM) {
                      ce = ce as OWLQuantifiedRestriction
                      qualities.add(getName(ce.getFiller()))
                    }
                  }
                } else if (prop in ["mp/mp-equivalent-axioms-subq#exists_during", "#during"]) { // exists-during (modified/intersect of E2)
                  during << filler
                } else if (prop == "BFO_0000051") { // has-part: treat as intersection ( :( )
                  haspart << filler
                } else if (prop == "BFO_0000050") { // part-of (E and part-of some X)
                  po << filler
                  filler.each { cj ->
                    if (cj.isClassExpressionLiteral()) {
                      def cjName = getName(cj);
                      if (cjName.startsWith('GO')) {
                        q << cjName;
                      } else if (cjName.startsWith('PATO')) {
                        qualities.add(cjName)
                      }
                    } else if (cj.getClassExpressionType() == ClassExpressionType.OBJECT_SOME_VALUES_FROM) {
                      cj = cj as OWLQuantifiedRestriction
                      prop = getName(cj.getProperty())
                      filler = cj.getFiller().asConjunctSet()
                      if (prop == "BFO_0000050") {
                        filler.each { cnj ->
                          if (cnj.isClassExpressionLiteral()) {
                            q << getName(cnj)
                          }
                        }
                      } else if (prop in ["RO_0002503", "#towards"]) { // towards
                        e2 << filler
                      } else if (prop in ["mp/mp-equivalent-axioms-subq#has_central_participant", "#has-central-participant"]) { // has-central-participant (?)
                        centralparticipant << filler
                      } else if (prop in ["mp-equivalent-axioms-subq#results_from", "#results-from"]) { // has-central-participant (?)
                        resultsfrom << filler
                      } else if (prop in ["BFO_0000066","mp/mp-equivalent-axioms-subq#occurs_in", "#occurs-in"]) { // occurs-in: make modifier to E (E occurs in ...)
                        occursin << filler
                      } else if (prop in ["mp/mp-equivalent-axioms-subq#exists_during", "#during"]) { // exists-during (modified/intersect of E2)
                        during << filler
                      } else {
                        println("Ignored property: $prop")
                      }
                    }
                  }
                } else if (prop in ["mp/mp-equivalent-axioms-subq#has_central_participant", "#has-central-participant"]) { // has-central-participant (?)
                  centralparticipant << filler
                } else if (prop in ["mp-equivalent-axioms-subq#results_from", "#results-from"]) { // has-central-participant (?)
                  resultsfrom << filler
                } else if (prop in ["BFO_0000066","mp/mp-equivalent-axioms-subq#occurs_in", "#occurs-in"]) { // occurs-in: make modifier to E (E occurs in ...)
                  occursin << filler
                } else {
                  println "Ignoring $cl: " + prop
                }
              } else {
                println("Ignored conjunction: $cl $conj")
              }
            }
          }
        }
      }
    }
    for (def item: q) {
      def pheno = 0
      if (item.startsWith("GO") && !(item in ignored_gos)) {
        allQual.addAll(qualities)
        for (def qual: qualities) {
          if (qual in up) {
            pheno = 1
            break
          }
          if (qual in down) {
            pheno = -1
            break
          }
        }
        out.println("$clName\t$item\t$pheno")
      }
    }
    Expando exp = new Expando()
    exp.cl = getName(cl)
    exp.e = e
    exp.e2 = e2
    // exp.q = q
    exp.ihp = ihp
    exp.mod = modifier
    exp.occ = occursin
    exp.hp = haspart
    exp.during = during
    exp.hasquality = hasquality
    exp.centralparticipant = centralparticipant
    exp.resultsfrom = resultsfrom
    // println(exp)
  }
}

out.flush()
out.close()
