#!/usr/bin/env python
import numpy as np
import pandas as pd
import click as ck
from utils import EXP_CODES, get_ontology, get_anchestors


@ck.command()
def main():
    deepgo_pred_stats()
    # no_pheno_genes()
    
    # annotation_stats('data/goa_human.gaf')

def no_pheno_genes():
    preds = set()
    annots = set()
    with open('data/predictions_human_filtered.txt') as f:
        for line in f:
            it = line.strip().split('\t')
            preds.add(it[0])
    with open('data/human_annotations.tab') as f:
        for line in f:
            it = line.strip().split('\t')
            annots.add(it[0])
    print(len(preds - annots))
    


def deepgo_pred_stats():
    overlap = set()
    with open('data/overlap.txt') as f:
        for line in f:
            line = line.strip()
            overlap.add(line)
    c = 0
    with open('data/human_deepannots.tab') as f:
        for line in f:
            it = line.strip().split('\t')
            if len(set(it[1:]).intersection(overlap)) > 0:
                c += 1
    print(c)
    
def deepgo_stats():
    df = pd.read_pickle('data/bp.pkl')
    functions = set(df['functions'].values)
    n = 0
    rules = set()
    with open('data/rules_prop.txt') as f:
        for line in f:
            it = line.strip().split('\t')
            rules.add(it[0].replace('_', ':'))

    print('Functions: ', len(functions))
    print('Rules: ', len(rules))
    inter = functions.intersection(rules)
    with open('data/overlap.txt', 'w') as f:
        for go_id in inter:
            f.write(go_id + '\n')

    print('Overlap: ', len(inter))
    go = get_ontology('data/go.obo')
    for go_id in list(inter):
        inter |= get_anchestors(go, go_id)
    print(len(inter))
    res = list()
    for func in functions:
        if func in inter:
            res.append(func)
    print(len(res))
    df = pd.DataFrame({'functions': res})
    df.to_pickle('data/phenogo.pkl')
    

def annotation_stats(filename):
    prots = set()
    annots_num = 0
    with open(filename) as f:
        for line in f:
            if line.startswith('!'):
                continue
            it = line.strip().split('\t')
            if it[3] == 'NOT' or it[6] not in EXP_CODES:
                continue
            if len(it) > 15 and it[15].find('CL:') != -1:
                print(it[15])
                continue
            prots.add(it[1])
            annots_num += 1
    print(len(prots), annots_num)
    

if __name__ == '__main__':
    main()
