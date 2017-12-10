import numpy as np
from collections import deque

EXP_CODES = set(['EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP', 'TAS', 'IC'])


class DataGenerator(object):

    def __init__(self, batch_size, num_outputs):
        self.batch_size = batch_size
        self.num_outputs = num_outputs

    def fit(self, inputs, targets):
        self.start = 0
        self.inputs = inputs
        self.targets = targets
        self.size = len(self.inputs)
        if isinstance(self.inputs, tuple) or isinstance(self.inputs, list):
            self.size = len(self.inputs[0])
        self.has_targets = targets is not None

    def __next__(self):
        return self.next()

    def reset(self):
        self.start = 0

    def next(self):
        if self.start < self.size:
            if self.has_targets:
                output = []
                labels = self.targets
                for i in range(self.num_outputs):
                    output.append(
                        labels[self.start:(self.start + self.batch_size), i])
            if isinstance(self.inputs, tuple) or isinstance(self.inputs, list):
                res_inputs = []
                for inp in self.inputs:
                    res_inputs.append(
                        inp[self.start:(self.start + self.batch_size)])
            else:
                res_inputs = self.inputs[self.start:(
                    self.start + self.batch_size)]
            self.start += self.batch_size
            if self.has_targets:
                return (res_inputs, output)
            return res_inputs
        else:
            self.reset()
            return self.next()


def get_ontology(filename='hp.obo'):
    # Reading Ontology from OBO Formatted file
    ont = dict()
    obj = None
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line == '[Term]':
                if obj is not None:
                    ont[obj['id']] = obj
                obj = dict()
                obj['is_a'] = list()
                obj['is_obsolete'] = False
                continue
            elif line == '[Typedef]':
                obj = None
            else:
                if obj is None:
                    continue
                l = line.split(": ")
                if l[0] == 'id':
                    obj['id'] = l[1]
                elif l[0] == 'is_a':
                    obj['is_a'].append(l[1].split(' ! ')[0])
                elif l[0] == 'name':
                    obj['name'] = l[1]

                elif l[0] == 'is_obsolete' and l[1] == 'true':
                    obj['is_obsolete'] = True
    if obj is not None:
        ont[obj['id']] = obj
    for node_id in ont.keys():
        if ont[node_id]['is_obsolete']:
            del ont[node_id]
    for node_id, val in ont.iteritems():
        if 'children' not in val:
            val['children'] = set()
        for n_id in val['is_a']:
            if n_id in ont:
                if 'children' not in ont[n_id]:
                    ont[n_id]['children'] = set()
                ont[n_id]['children'].add(node_id)

    return ont


def get_anchestors(ont, node_id):
    anchestors = set()
    q = deque()
    q.append(node_id)
    while(len(q) > 0):
        n_id = q.popleft()
        anchestors.add(n_id)
        for parent_id in ont[n_id]['is_a']:
            if parent_id in ont:
                q.append(parent_id)
    return anchestors


def get_parents(ont, node_id):
    parents = set()
    for parent_id in ont[node_id]['is_a']:
        if parent_id in ont:
            parents.add(parent_id)
    return parents


def get_subset(ont, node_id):
    subset = set()
    q = deque()
    q.append(node_id)
    while len(q) > 0:
        n_id = q.popleft()
        subset.add(n_id)
        for ch_id in ont[n_id]['children']:
            q.append(ch_id)
    return subset

