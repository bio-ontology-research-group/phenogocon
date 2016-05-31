from org.semanticweb.elk.owlapi import ElkReasonerFactory
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI
from org.semanticweb.owlapi.reasoner import ConsoleProgressMonitor, SimpleConfiguration
from org.semanticweb.owlapi.search import EntitySearcher


gobasic = "go-basic.obo"

manager = OWLManager.createOWLOntologyManager()
factory = manager.getOWLDataFactory()
ontset = set()
ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "mp.owl")))
ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "hp.owl")))
ontset.add(manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "fypo.owl")))
ont = manager.createOntology(IRI.create("http://aber-owl.net/phenotype-input.owl"), ontset)

progressMonitor = ConsoleProgressMonitor()
config = SimpleConfiguration(progressMonitor)
reasoner = ElkReasonerFactory().createReasoner(ont, config)


class Species:
    name = ""
    filename = ""
    columns = (-1, -1)
    def __init__(self, name, filename, columns):
        self.name = name
        self.filename = filename
        self.columns = columns
        
speciesList = []
# put your species here, each instance is [name, filename, columns (gene, pheno)]
speciesList.append(Species("MP", "MGI_GenePheno.rpt", (6, 4)))
speciesList.append(Species("HP", "HP_genepheno.tab", (0, 1)))
speciesList.append(Species("FYPO", "FYPO_genepheno.tab", (0, 1)))
speciesnames = ["MP", "HP", "FYPO"]

def create_class(s):
    return factory.getOWLClass(IRI.create(s))

def formatClassNames(s):
    s = s.replace("http://purl.obolibrary.org/obo/","")
    s = s.replace("<","")
    s = s.replace(">","")
    s = s.replace("_",":")
    return s


def rev_formatClassNames(s):
    s = s.replace(":", "_")
    s = "http://purl.obolibrary.org/obo/" + s
    return s


def hp_gene_mim_pheno():
    # uses the omim data to create a database of genes and phenos for HP, without the mim    
    mim2gene = dict()
    with open("diseases_to_genes.txt", 'r') as f:
        for line in f:
            if not line or line[0] in "#!":
                continue
            tabs = line.strip('\n').split('\t')
            if len(tabs) < 3:
                continue
            mim = tabs[0]
            gene = tabs[2]
            if mim not in mim2gene:
                mim2gene[mim] = set()
            mim2gene[mim].add(gene)
        
    with open("phenotype_annotation.tab", 'r') as f:
        with open("HP_genepheno.tab", 'w') as g:
            for line in f:
                if not line or line[0] in "#!":
                    continue
                tabs = line.split('\t')
                if tabs[0] != "OMIM":
                    continue
                pheno = tabs[4]
                mim = tabs[5]
                if "OMIM" not in mim:
                    continue
                if mim not in mim2gene:
                    continue      
                for gene in mim2gene[mim]:
                    g.write("%s\t%s\n" % (gene, pheno))

def fypo_gene_description_pheno():
    # maps genes to phenos via descriptions
    manager = OWLManager.createOWLOntologyManager()
    factory = manager.getOWLDataFactory()
    ontology = manager.loadOntologyFromOntologyDocument(IRI.create("file:" + "fypo.owl"))
    clset = ont.getClassesInSignature(True)
    desc2pheno = dict()
    for cl in clset:
        id = ""
        synonyms = []
        for anno in EntitySearcher.getAnnotations(cl.getIRI(), ontology):
            s = anno.getProperty().toStringID()
            if s == "http://www.geneontology.org/formats/oboInOwl#hasExactSynonym":
                synonyms.append(anno.getValue().getLiteral())
            elif s == "http://www.geneontology.org/formats/oboInOwl#id":
                id = anno.getValue().getLiteral()
        for syn in synonyms:
            desc2pheno[syn] = id
    
    with open("phenotype_data.tab", 'r') as f:
        with open("FYPO_genepheno.tab", 'w') as g:
            for line in f:
                if not line or line[0] in "#!":
                    continue
                tabs = line.split('\t')
                gene = tabs[2]
                desc = tabs[9]
                if gene and desc in desc2pheno: # TODO some gene ids are blank, then need to use gene name
                    g.write("%s\t%s\n" % (gene, desc2pheno[desc]))
                elif not gene:
                    pass
                

go = "http://purl.obolibrary.org/obo/GO_"
pheno2gofile = "pheno2go.txt"
down = ["PATO:0000462", "PATO:0000381", "PATO:0000911", "PATO:0000297", "PATO:0001511", "PATO:0001507"]
abnormal = ["PATO:0000001"]
up = ["PATO:0000912"]

gene2pheno = dict() # maps gene -> {pheno}
print "Building gene2pheno"
for species in speciesList:
    
    if species.name == "HP":
        # eliminate mim
        hp_gene_mim_pheno()
        
    if species.name == "FYPO":
        # eliminate descriptions
        fypo_gene_description_pheno()
        
    with open(species.filename, 'r') as f:
        for line in f:
            if not line or line[0] in "!#":
                continue
            tabs = line.strip('\n').split('\t')
            gene = tabs[species.columns[0]]
            pheno = tabs[species.columns[1]]
            if gene not in gene2pheno:
                gene2pheno[gene] = set()
            gene2pheno[gene].add(pheno)

    
# build pheno2go
print "Building pheno2go..."
pheno2go = dict()
for line in open(pheno2gofile, 'r'):
    tabs = line.strip('\n').split('\t')
    pheno = formatClassNames(tabs[0])
    gos = tabs[1]
    if pheno not in pheno2go:
        pheno2go[pheno] = set()
    if tabs[2] in down:
        pheno2go[pheno].add((gos, "down"))
    elif tabs[2] in up:
        pheno2go[pheno].add((gos, "up"))
    elif tabs[2] in abnormal: # abnormal
        pheno2go[pheno].add((gos, "abnormal"))


class Stats:
    stats = dict()
    def __init__(self, speciesList):
        self.stats = dict()
        for species in speciesList:
            self.stats[species.name] = dict()
            for stat in ["consistent", "consistent up/down", "inconsistent up/down", "total"]:
                self.stats[species.name][stat] = 0
            
    def increment(self, speciesname, stat):
        self.stats[speciesname][stat] += 1
        
    def printStats(self):
        for speciesname in self.stats:
            print "\nSpecies %s:" % speciesname
            for stat in self.stats[speciesname]:
                print "%s: %d" % (stat, self.stats[speciesname][stat])
            hits = self.stats[speciesname]["consistent up/down"]
            misses = self.stats[speciesname]["inconsistent up/down"]
            if hits + misses > 0:
                print "accuracy = %d / %d = %f" % (hits, hits + misses, (hits+0.0)/(hits + misses))
            print "unknown: %d" % (self.stats[speciesname]["total"] - self.stats[speciesname]["consistent"])
    
stats1 = Stats(speciesList)

openset = set()
closed = set()
mflag, hflag, fflag = False, False, False
# read and compare inferred phenos with database data
print "Reading inferred phenos"
with open("inferred-phenos.txt", 'r') as f:
    for line in f:
        tabs = line.strip('\n').split('\t')
        gene = tabs[0]
        pheno = tabs[1]
        direction = tabs[2]
        go1 = tabs[3]
        go2 = tabs[4]
        
        speciesname = pheno[:pheno.find(':')]
        if speciesname not in speciesnames:
            continue
        
        if direction == "abnormal":
            gotemp = (gene, go1, "abnormal")
        else:
            gotemp = (gene, go2)
        if gotemp in closed:
            continue
        
        if gotemp not in openset:
            openset.add(gotemp)
            stats1.increment(speciesname, "total")
        
        if gene in gene2pheno:
            phenoclass = create_class(rev_formatClassNames(pheno))
            subclasses = reasoner.getSubClasses(phenoclass, False).getFlattened()
            for subpheno in subclasses:
                if formatClassNames(subpheno.toString()) in gene2pheno[gene]:
                    stats1.increment(speciesname, "consistent")
                    
                    if speciesname == "MP" and not mflag:
                        mflag = True
                        print line
                        
                    if speciesname == "HP" and not hflag:
                        hflag = True
                        print line
                        
                    if speciesname == "FYPO" and not fflag:
                        fflag = True
                        print line
                    
                    if go2 != "NONE":
                        stats1.increment(speciesname, "consistent up/down")
                    closed.add(gotemp)
                    break

closed = set()

mflag, hflag, fflag = False, False, False

print "Reading negated inferred phenos"
with open("neg-inferred-phenos.txt", 'r') as f:
    for line in f:
        tabs = line.strip('\n').split('\t')
        gene = tabs[0]
        pheno = tabs[1]
        direction = tabs[2]
        go1 = tabs[3]
        go2 = tabs[4]
        
        if direction == "abnormal":
            continue
        else:
            gotemp = (gene, go2)
        if gotemp in closed:
            continue
        
        speciesname = pheno[:pheno.find(':')]
        if speciesname not in speciesnames:
            continue   
             
        if gene in gene2pheno:
            phenoclass = create_class(rev_formatClassNames(pheno))
            subclasses = reasoner.getSubClasses(phenoclass, False).getFlattened()
            for subpheno in subclasses:
                if formatClassNames(subpheno.toString()) in gene2pheno[gene]:
                    
                    if speciesname == "MP" and not mflag:
                        mflag = True
                        print line
                        
                    if speciesname == "HP" and not hflag:
                        hflag = True
                        print line
                        
                    if speciesname == "FYPO" and not fflag:
                        fflag = True
                        print line
                    
                    stats1.increment(speciesname, "inconsistent up/down")
                    closed.add(gotemp)
                    break
        
stats1.printStats()
    
print "\nProgram terminated"
