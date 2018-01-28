#!/usr/bin/env python

import pandas as pd
import numpy as np
import click as ck
from sklearn.metrics import roc_curve, auc
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from scipy.stats import spearmanr, pearsonr, wilcoxon, rankdata

plot_title = 'Human Gene-Disease association predictions'
plot_filename = 'GD-human.pdf'

@ck.command()
def main():
    plot_rocs()


def plot_rocs():
    plt.figure()
    df = pd.read_pickle('data/sim_gd_human.pkl')
    fpr = df['fpr'].values
    tpr = df['tpr'].values
    roc_auc = auc(fpr, tpr)
    print(roc_auc)
    plt.plot(
        fpr,
        tpr,
        label='Real annotation ROC curve (area = %0.3f)' % roc_auc)
    df = pd.read_pickle('data/sim_gd_human_only_pred.pkl')
    fpr = df['fpr'].values
    tpr = df['tpr'].values
    roc_auc = auc(fpr, tpr)
    print(roc_auc)
    plt.plot(
        fpr,
        tpr,
        label='Only predictions ROC curve (area = %0.3f)' % roc_auc)
    
    df = pd.read_pickle('data/sim_gd_human_with_pred.pkl')
    fpr = df['fpr'].values
    tpr = df['tpr'].values
    roc_auc = auc(fpr, tpr)
    print(roc_auc)
    plt.plot(
        fpr,
        tpr,
        label='With predictions ROC curve (area = %0.3f)' % roc_auc)
    # df = pd.read_pickle('data/sim_ppi_human_deep_only.pkl')
    # fpr = df['fpr'].values
    # tpr = df['tpr'].values
    # roc_auc = auc(fpr, tpr)
    # print(roc_auc)
    # plt.plot(
    #     fpr,
    #     tpr,
    #     label='DeepGO and Only predictions ROC curve (area = %0.3f)' % roc_auc)
    
    # df = pd.read_pickle('data/sim_ppi_human_deep_with.pkl')
    # fpr = df['fpr'].values
    # tpr = df['tpr'].values
    # roc_auc = auc(fpr, tpr)
    # print(roc_auc)
    # plt.plot(
    #     fpr,
    #     tpr,
    #     label='DeepGO and With predictions ROC curve (area = %0.3f)' % roc_auc)
    
    
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
