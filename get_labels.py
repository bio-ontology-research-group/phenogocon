#!/usr/bin/env python

import requests
import click as ck
import pandas as pd

@ck.command()
def main():
    df = pd.read_pickle('data/phenogo.pkl')
    
    for go_id in df['functions']:
        ids = [
            '<http://purl.obolibrary.org/obo/%s>' % go_id.replace(':', '_'),
        ]
        params = {'iri': ids, 'ontology': 'PhenomeNET'}
        r = requests.get('http://10.254.145.9/api/classes/', params=params)
        result = r.json()['result']
        print('%s\t%s' % (go_id, result[ids[0]]['label']))

    # with open('mouse_incon.tab') as f:
    #     for line in f:
    #         it = line.strip().split('\t')
    #         ids = [
    #             '<http://purl.obolibrary.org/obo/%s>' % it[1],
    #             '<http://purl.obolibrary.org/obo/%s>' % it[2],
    #         ]
    #         params = {'iri': ids, 'ontology': 'PhenomeNET'}
    #         r = requests.get('http://10.254.145.9/api/classes/', params=params)
    #         result = r.json()['result']
    #         print('%s\t%s\t%s\t%s\t%s' % (it[0], it[1], result[ids[0]]['label'], it[2], result[ids[1]]['label']))


if __name__ == '__main__':
    main()
