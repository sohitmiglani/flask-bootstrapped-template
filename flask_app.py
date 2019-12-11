# importing general extensions of flask here
from flask import Flask, session, render_template, request, flash, url_for, redirect, send_file, Response, make_response
from io import BytesIO, StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import flask
from flask_bootstrap import Bootstrap
import app_functions # importing the app_functions.py file to have all the functions ready
from app_functions import __version__
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import seaborn as sns
plt.style.use('ggplot')
plt.switch_backend('Agg')

# The code for setting up a user session in flask and securing it with a secret_key is already installed below.
# You can jump directly to building your functions, and collecting HTML inputs for processing.

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = True
app.config["SECRET_KEY"] = app_functions.random_id(50)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Bootstrap(app)

@app.route("/", methods=["GET", "POST"])
def home():

    if 'status' not in session:
        session['input_data'] = ''

    if request.method == "POST":
        if request.form['submit_button'] == 'submit_data':
            session['specimen'] = request.form["specimen"]
            session['workflow'] = request.form["workflow"]
            session['number_of_samples'] = request.form['number_of_samples']
            input_file = request.files["metadata"]
            session['input_data'] = input_file.stream.read().decode("utf-8")

            input_annotation = request.files["annotation"]
            session['annotation'] = input_annotation.stream.read().decode("utf-8")

            if session['workflow'] == 'complete':
                flash('The workflow for the complete analysis is not available yet. Only QC and visualisations are available.')
            else:
                return redirect(url_for('results'))

    return render_template('home.html',
                           version=__version__)

@app.route("/scatter.png", methods=["GET", "POST"])
def scatter():
    dataframe = pd.read_csv(StringIO(session['input_data']))

    sns.set()

    fig2, ax2 = plt.subplots()

    for i in range(int(session['number_of_samples'])):
        plt.scatter( list(dataframe['Sample'+str(i+1)]) ,[i+1 for _ in range(len(dataframe))] )

    plt.ylabel('Samples')
    plt.xlabel('Gene Count Distributions')
    plt.title('Scatter Plot of Gene Counts for comparative analysis', fontsize= 15)

    canvas = FigureCanvas(fig2)
    img2 = BytesIO()
    fig2.savefig(img2)
    img2.seek(0)

    return send_file(img2, mimetype='image/png')

@app.route("/results", methods=["GET", "POST"])
def results():

    dataframe = pd.read_csv(StringIO(session['input_data']))
    analysis_data = []

    import os
    cwd = os.getcwd()

    for i in range(int(session['number_of_samples'])):
        analysis_data.append(list(dataframe['Sample'+str(i+1)]))

    model = PCA(n_components=2)
    output = model.fit_transform(analysis_data)

    sns.set()
    plt.figure()
    number_of_samples = int(session['number_of_samples'])
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
    plt.xticks(np.arange(number_of_samples+1),range(number_of_samples))
    plt.title('Box Plots of Gene Counts for comparative analysis', fontsize= 15)
    plt.savefig(cwd + '/static/images/box_plot.png')

    medians1 = []
    medians2 = []

    condition1 = []
    condition2 = []

    annotation = pd.read_csv(StringIO(session['annotation']))

    for i in range(number_of_samples):
        if annotation['Condition'][i] == 1:
            condition1.append(annotation['Sample'][i])
        elif annotation['Condition'][i] == 2:
            condition2.append(annotation['Sample'][i])

    import statistics

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

    return render_template('results.html',
                           version=__version__)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.errorhandler(404)
def page_not_found(e):
    # the flash utlity flashes a message that can be shown on the main HTML page
    flash('The URL you entered does not exist. You have been redirected to the home page')
    return redirect(url_for('home'))
