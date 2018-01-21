#!/usr/bin/env python

import click as ck
import pandas as pd
import numpy as np

score = 0.24

@ck.command()
def main():
    mouse_annots()
    human_annots()


def mouse_annots():
    mapping = dict()

    with open('data/mgi2uniprot.tab') as f:
        for line in f:
            it = line.strip().split('\t')
            if len(it) == 2:
                if it[1] not in mapping:
                    mapping[it[1]] = list()
                mapping[it[1]].append(it[0])

    df = pd.read_pickle('data/phenogo.pkl')
    funcs = df['functions'].values

    df = pd.read_pickle('data/mouse-phenogo-preds.pkl')
    annots = dict()
    w = open('data/mouse_deepannots.tab', 'w')
    for i, row in df.iterrows():
        if row['proteins'] in mapping:
            gene = mapping[row['proteins']]
            for s, go_id in zip(row['predictions'], funcs):
                if s >= score:
                    for gn in gene:
                        if gn not in annots:
                            annots[gn] = set()
                        annots[gn].add(go_id)
    for gene, gos in annots.items():
        w.write(gene)
        for go_id in gos:
            w.write('\t' + go_id)
        w.write('\n')
    w.close()


def human_annots():
    mapping = dict()

    with open('data/human2uni.tab') as f:
        for line in f:
            it = line.strip().split('\t')
            if len(it) == 2:
                if it[0] not in mapping:
                    mapping[it[0]] = list()
                mapping[it[0]].append(it[1])

    df = pd.read_pickle('data/phenogo.pkl')
    funcs = df['functions']
    annots = dict()
    w = open('data/human_deepannots.tab', 'w')
    df = pd.read_pickle('data/human-phenogo-preds.pkl')
    for i, row in df.iterrows():
        if row['proteins'] in mapping:
            gene = mapping[row['proteins']]
            for s, go_id in zip(row['predictions'], funcs):
                if s >= score:
                    for gn in gene:
                        if gn not in annots:
                            annots[gn] = set()
                        annots[gn].add(go_id)
    for gene, gos in annots.items():
        w.write(gene)
        for go_id in gos:
            w.write('\t' + go_id)
        w.write('\n')
    w.close()
    
if __name__ == '__main__':
    main()
