#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import

import matplotlib as mpl
mpl.use('Agg')

import pandas as pd
import click as ck
import numpy as np
import sys
from sklearn.metrics import roc_curve, auc
from matplotlib import pyplot as plt
from scipy.stats import spearmanr, pearsonr, wilcoxon
import gzip


annots_file = 'data/mgi_annotations_only_pred.tab'
scores_file = 'data/sim_ppi_only_pred.txt'
plot_title = 'ROC Curve BMA Resnik - Mouse PPI Only Predictions'
plot_filename = "PPI-mouse-only-pred.pdf"

@ck.command()
def main():
    run()


def run():
    # gd = gene_disease()
    genes = load_mouse_genes()
    print(genes[:100])
    ppi = load_mouse_ppi()
    # diseases = load_diseases() 
    scores = load_scores()
    associations = list()
    for i in xrange(len(genes)):
        for j in xrange(len(genes)):
            if i == j:
                continue
            if genes[i] in ppi and genes[j] in ppi[genes[i]]:
                associations.append(1)
            else:
                associations.append(0)
    print(sum(associations))
    roc_auc = compute_roc(scores, associations)
    print('ROC AUC: ', roc_auc)


def load_ppi():
    res = dict()
    mapping = dict()
    with open('data/human2string.tab') as f:
        for line in f:
            it = line.strip().split('\t')
            st = it[0]
            mgi = it[1]
            if st not in mapping:
                mapping[st] = list()
            mapping[st].append(mgi)
    with gzip.open('data/9606.protein.links.v10.5.txt.gz') as f:
        next(f)
        for line in f:
            it = line.strip().split()
            p1, p2, score = it[0], it[1], int(it[2])
            if score >= 300 and p1 in mapping and p2 in mapping:
                p1 = mapping[p1]
                p2 = mapping[p2]
                for g1 in p1:
                    for g2 in p2:
                        if g1 not in res:
                            res[g1] = set()
                        if g2 not in res:
                            res[g2] = set()
                        res[g1].add(g2)
                        res[g2].add(g1)
    return res


def load_mouse_ppi():
    res = dict()
    mapping = dict()
    with open('data/mgi2string.tab') as f:
        for line in f:
            it = line.strip().split('\t')
            st = it[0]
            mgi = it[1]
            if st not in mapping:
                mapping[st] = list()
            mapping[st].append(mgi)
    with gzip.open('data/10090.protein.links.v10.5.txt.gz') as f:
        next(f)
        for line in f:
            it = line.strip().split()
            p1, p2, score = it[0], it[1], int(it[2])
            if score >= 300 and p1 in mapping and p2 in mapping:
                p1 = mapping[p1]
                p2 = mapping[p2]
                for g1 in p1:
                    for g2 in p2:
                        if g1 not in res:
                            res[g1] = set()
                        if g2 not in res:
                            res[g2] = set()
                        res[g1].add(g2)
                        res[g2].add(g1)
    return res

        
def load_homo():
    res = dict()
    with open('data/hom_mouse.tab', 'r') as f:
        for line in f:
            items = line.strip().split('\t')
            res[items[0]] = items[5]
    return res


def gene_disease():
    gd = dict()
    # homo = load_homo()
    with open('data/mgi_omim.tab') as f:
        for line in f:
            if line.startswith('#'):
                continue
            items = line.strip().split('\t')
            dis_id = items[0]
            # homo_id = items[2]
            # if homo_id not in homo:
            #     continue
            gene_id = items[7]
            if gene_id not in gd:
                gd[gene_id] = set()
            gd[gene_id].add(dis_id)
            if dis_id not in gd:
                gd[dis_id] = set()
            gd[dis_id].add(gene_id)
    return gd


def load_scores():
    scores = list()
    with open(scores_file) as f:
        for line in f:
            scores.append(float(line.strip()))
    scores = (np.array(scores) - min(scores)) / (max(scores) - min(scores))
    # return scores
    scores_without = list()
    i = 0
    c = 0
    while i * i < len(scores):
        j = 0
        while j * j < len(scores):
            if i != j:
                scores_without.append(scores[c])
            j += 1
            c += 1
        i += 1
    print(i, j)
    return scores_without


def load_genes():
    mapping = dict()
    with open('data/genes_to_phenotype.txt') as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            mapping[it[1]] = it[0]
    genes = list()
    with open(annots_file) as f:
        for line in f:
            items = line.strip().split('\t')
            if items[0] in mapping:
                genes.append(mapping[items[0]])
            else:
                genes.append(items[0])
    return genes


def load_mouse_genes():
    genes = list()
    with open(annots_file) as f:
        for line in f:
            items = line.strip().split('\t')
            genes.append(items[0])
    return genes

def load_diseases():
    diseases = list()
    with open('data/omim_annotations.tab') as f:
        for line in f:
            items = line.strip().split('\t')
            diseases.append(items[0])
    return diseases


def compute_roc(scores, test):
    # Compute ROC curve and ROC area for each class
    fpr, tpr, _ = roc_curve(test, scores)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(
        fpr,
        tpr,
        label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(plot_title)
    plt.legend(loc="lower right")
    plt.savefig(plot_filename)
    return roc_auc


if __name__ == '__main__':
    main()
