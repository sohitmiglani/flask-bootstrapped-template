# This .py file houses all the major functions you'll use in your flask app.
# Have all the functions here and then import them in the flask_app.py file.

from flask import session
import pandas # import all the required libraries here
import random
import os
import statistics
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import math
from scipy.stats import ks_2samp


__version__ = "1.0.1" # specify a version here in the backend

def random_id(length): # This function has two doctests inside it to give an example on how to make doctests
    """
    Creates a random configuration key for the session - for safety of session variables.

    >>> len(random_id(50)) == 50
    True

    >>> random_id('hello')
    Traceback (most recent call last):
        ...
    TypeError: The input must be a positive integer.

    """
    if type(length) != int or length < 1:
        raise TypeError('The input must be a positive integer.')

    choices = '0123456789abcdefghijklmnopqrstuvwxyz'

    id = ''
    for _ in range(length):
        id += random.choice(choices)
    return id


def make_all_visualisations(dataframe, annotation):
    session['initial_number'] = len(dataframe)

    cwd = os.getcwd()
    samples = [x for x in dataframe.columns if x not in ['log2f','se','p_values','gene']]

    for i in range(len(dataframe)):
        if dataframe[samples[0]][i] == 0:
            dataframe = dataframe.drop(i)

    session['final_number'] = len(dataframe)
    dataframe.index = range(len(dataframe))

    try:
        os.remove(cwd + '/static/images/ml_plot.png')
        os.remove(cwd + '/static/images/scatter.png')
        os.remove(cwd + '/static/images/box_plot.png')
        os.remove(cwd + '/static/images/median_plot.png')
    except:
        pass

    try:
        os.remove(cwd + '/static/images/volcano.png')
        os.remove(cwd + '/static/images/gene_map.png')
        os.remove(cwd + '/static/images/heatmap.png')
    except:
        pass

    analysis_data = []
    cwd = os.getcwd()

    number_of_samples = len(samples)

    for i in range(number_of_samples):
        analysis_data.append(list(dataframe[samples[i]]))

    model = PCA(n_components=2)
    output = model.fit_transform(analysis_data)

    first_var = round(model.explained_variance_ratio_[0]*100,2)
    second_var = round(model.explained_variance_ratio_[1]*100,2)

    sns.set()
    plt.figure()
    for i in range(number_of_samples):
        plt.plot(output[i][0],output[i][1], marker='o', label=samples[i])

    plt.ylabel('Second Component of PCA')
    plt.xlabel('First Component of PCA')
    plt.title('Quality Check: Clustering of the samples in PCA ' + '\n', fontsize= 15)
    plt.legend()
    plt.savefig(cwd + '/static/images/ml_plot.png')

    plt.figure()
    for i in range(number_of_samples):
        plt.scatter(list(dataframe[samples[i]]) ,[i+1 for _ in range(len(dataframe))] )
    plt.ylabel('Samples')
    plt.xlabel('Gene Count Distributions')
    plt.yticks(np.arange(number_of_samples+1),range(number_of_samples+1))
    plt.title('Scatter Plot of Gene Counts for comparative analysis', fontsize= 15)
    plt.savefig(cwd + '/static/images/scatter.png')

    plt.figure()
    plt.boxplot(analysis_data)
    plt.ylabel('Transcript Counts for Log Transformed Gene Counts')
    plt.xlabel('Samples')
    plt.xticks(np.arange(number_of_samples+1),range(number_of_samples+1))
    plt.title('Box Plots of Gene Counts for comparative analysis', fontsize= 15)
    plt.savefig(cwd + '/static/images/box_plot.png')

    medians1 = []
    medians2 = []

    means1 = []
    means2 = []

    condition1 = []
    condition2 = []

    p_values = []

    for i in range(number_of_samples):
        if list(annotation['condition'])[i] == 1:
            condition1.append(annotation['sample'][i])
        elif list(annotation['condition'])[i] == 2:
            condition2.append(annotation['sample'][i])

    for i in list(dataframe.index):
        first = []
        second = []

        for sample in condition1:
            first.append(dataframe[sample][i])
        for sample in condition2:
            second.append(dataframe[sample][i])

        medians1.append(statistics.median(first))
        medians2.append(statistics.median(second))

        p_value = list(ks_2samp(first, second))[1]

        if p_value > 0.5:
            p_value = 1-p_value

        p_values.append(p_value)

        means1.append(np.mean(first))
        means2.append(np.mean(second))

    highest = max(medians1 + medians2)

    plt.figure()
    plt.scatter(medians1,medians2)
    plt.plot([0,highest],[0,highest],color='red',label='Normal expression')
    plt.ylabel('Median of Samples for Condition 2')
    plt.xlabel('Median of Samples for Condition 1')
    plt.title('Scatter plot of median gene counts for Condition 1 Vs. Condition 2', fontsize= 15)
    plt.legend()
    plt.savefig(cwd + '/static/images/median_plot.png')

    filtered_genes = []

    if number_of_samples < 3:
        session['stats'] = False
    else:
        if 'log2f' not in dataframe.columns:
            dataframe['p_values'] = p_values
            log2f = []

            for i in range(len(dataframe)):
                if means1[i] == 0 or means2[i] == 0:
                    log2f.append(0)
                else:
                    log2f.append(math.log(abs(means2[i]/means1[i]),2))
            dataframe['log2f'] = log2f

        plt.figure()
        plt.scatter(dataframe['log2f'], dataframe['p_values'])
        plt.ylabel('P-Values')
        plt.xlabel('Log Fold Change')
        plt.title('A Volcano plot of the p values against the log fold change.', fontsize= 15)
        plt.axvline(0)
        plt.savefig(cwd + '/static/images/volcano.png')

        filtered_names = []

        for i in list(dataframe.index):
            if dataframe['p_values'][i] < 0.025:
                if dataframe['log2f'][i] < -2 or dataframe['log2f'][i] > 2:
                    filtered_genes.append(i)
                    filtered_names.append(dataframe['gene'][i])

        half_num = int(number_of_samples//2)
        differences = []

        for index in filtered_genes:
            differences.append(means2[index]-means1[index])

        plt.figure(figsize=(10,20))
        plt.scatter(differences,range(1,len(differences)+1))
        plt.ylabel('Genes')
        plt.xlabel('Gene Count Differences (Condition 2 - Condition 1)')
        plt.yticks(range(1,len(differences)+1),filtered_names)
        plt.title('Gene Map of the differences between gene counts', fontsize= 15)
        plt.savefig(cwd + '/static/images/gene_map.png')
        session['stats'] = True

        new_dataframe = dataframe[samples].iloc[filtered_genes]

        plt.figure(figsize=(10,20))
        sns.heatmap(new_dataframe)
        plt.title('Heatmap of the gene counts for filtered genes')
        plt.ylabel('Gene Counts')
        plt.yticks(range(1,len(differences)+1),filtered_names)
        plt.savefig(cwd + '/static/images/heatmap.png')

    return first_var, second_var, len(filtered_genes)
