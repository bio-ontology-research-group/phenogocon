#!/usr/bin/env python
import numpy as np
import pandas as pd
import click as ck
from utils import EXP_CODES, get_ontology, get_anchestors


@ck.command()
def main():
    deepgo_stats()

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
            prots.add(it[1])
            annots_num += 1
    print(len(prots), annots_num)
    

if __name__ == '__main__':
    main()
