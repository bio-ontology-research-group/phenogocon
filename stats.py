#!/usr/bin/env python
import numpy as np
import pandas as pd
import click as ck
from utils import EXP_CODES


@ck.command()
def main():
    filename = 'data/goa_human.gaf'
    annotation_stats(filename)


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
