# PhenoGOCon

## Ontology-based validation and identification of regulatory phenotypes

Collection of groovy and python scripts used for analysis and evaluation
of predicting HPO and MPO phenotypes from GO functions for mouse and human


## Data

* pheno2go.txt - Correspondence of Phenotype and GO classes extracted
  using logical definitions in PhenomeNET ontology

* rules.txt - Set of generated rules for regulatory phenotypes and
  abnormalities of biological processes. Includes inconsistency checking rules

* rules_prop.txt - Set of generated rules for regulatory phenotypes and
  abnormalities of biological processes propagated using GO structure.
  Includes inconsistency checking rules

## Scripts

* Pheno2GO.groovy - groovy script which is used to parse logical definitions of
  Phenotype classes and extract GO correspondent class

* InferPhenos.groovy - script for finding regulation classes and annotation rules

* HumanAnnotations.groovy, MouseAnnotations.groovy - scripts for preparing
  annotation files for mouse and human

* SimGDPairwise.groovy, SimPPIPairwise.groovy - for computing semantic similarity
  between sets of phenotypes for gene-disease and protein-protein interaction
  predictions

* Evaluate.groovy - script for comparing predictions with manual annotations

* performance.py - script which is used to compute performance of predictions

* deepannots.py - for generating DeepGO annotations 