# This .py file houses all the major functions you'll use in your flask app.
# Have all the functions here and then import them in the flask_app.py file.

import pandas # import all the required libraries here
import random
import os
import statistics
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA


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
    analysis_data = []
    cwd = os.getcwd()

    number_of_samples = len(dataframe.columns) - 4
    for i in range(number_of_samples):
        analysis_data.append(list(dataframe['Sample'+str(i+1)]))

    model = PCA(n_components=2)
    output = model.fit_transform(analysis_data)

    first_var = round(model.explained_variance_ratio_[0]*100,2)
    second_var = round(model.explained_variance_ratio_[1]*100,2)

    sns.set()
    plt.figure()

    for i in range(number_of_samples):
        plt.plot(output[i][0],output[i][1], marker='o', label='Sample'+str(i+1))

    plt.ylabel('Second Component of PCA')
    plt.xlabel('First Component of PCA')
    plt.title('Quality Check: Clustering of the samples in PCA', fontsize= 15)
    plt.legend()
    plt.savefig(cwd + '/static/images/ml_plot.png')

    plt.figure()
    for i in range(number_of_samples):
        plt.scatter( list(dataframe['Sample'+str(i+1)]) ,[i+1 for _ in range(len(dataframe))] )
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

    condition1 = []
    condition2 = []

    for i in range(number_of_samples):
        if list(annotation['Condition'])[i] == 1:
            condition1.append(annotation['Sample'][i])
        elif list(annotation['Condition'])[i] == 2:
            condition2.append(annotation['Sample'][i])

    for i in range(len(dataframe)):
        first = []
        second = []

        for sample in condition1:
            first.append(dataframe[sample][i])
        for sample in condition2:
            second.append(dataframe[sample][i])

        medians1.append(statistics.median(first))
        medians2.append(statistics.median(second))

    highest = max(medians1 + medians2)

    plt.figure()
    plt.scatter(medians1,medians2)
    plt.plot([0,highest],[0,highest],color='red',label='Normal expression')
    plt.ylabel('Median of Samples for Condition 2')
    plt.xlabel('Median of Samples for Condition 1')
    plt.title('Scatter plot of median gene counts for Condition 1 Vs. Condition 2', fontsize= 15)
    plt.legend()
    plt.savefig(cwd + '/static/images/median_plot.png')

    plt.figure()
    plt.scatter(dataframe['log2f'], dataframe['p_values'])
    plt.ylabel('P-Values')
    plt.xlabel('Log Fold Change')
    plt.title('A Volcano plot of the p values against the log fold change.', fontsize= 15)
    plt.axvline(0)
    plt.savefig(cwd + '/static/images/volcano.png')

    filtered_genes = []
    filtered_names = []

    for i in range(len(dataframe)):
        if dataframe['p_values'][i] < 0.05:
            if dataframe['log2f'][i] < -2 or dataframe['log2f'][i] > 2:
                filtered_genes.append(i)
                filtered_names.append(dataframe['gene'][i])

    half_num = int(number_of_samples//2)
    differences = []

    for index in filtered_genes:
        intermediate = []
        for sample_num in range(1,half_num+1):
            intermediate.append(dataframe['Sample' + str(sample_num + half_num)][index] - dataframe['Sample' + str(sample_num)][index])
        differences.append(intermediate)

    plt.figure()
    for i in range(len(differences)):
        plt.scatter(differences[i],[i+1 for _ in range(half_num)])
    plt.ylabel('Genes')
    plt.xlabel('Gene Count Differences (Condition 2 - Condition 1)')
    plt.yticks(range(1,len(differences)+1),filtered_names)
    plt.title('Gene Map of the differences between gene counts', fontsize= 15)
    plt.savefig(cwd + '/static/images/gene_map.png')

    new_dataframe = dataframe.iloc[filtered_genes,0:number_of_samples]
    plt.figure()
    sns.heatmap(new_dataframe)
    plt.title('Heatmap of the gene counts for filtered genes')
    plt.ylabel('Gene Counts')
    plt.yticks(range(1,len(differences)+1),filtered_names)
    plt.savefig(cwd + '/static/images/heatmap.png')

    return first_var, second_var, len(filtered_genes)
