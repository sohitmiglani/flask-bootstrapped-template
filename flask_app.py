# importing general extensions of flask here
from flask import Flask, session, render_template, request, flash, url_for, redirect, send_file, Response, make_response
from io import BytesIO, StringIO
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import flask
from flask_bootstrap import Bootstrap
import app_functions # importing the app_functions.py file to have all the functions ready
from app_functions import __version__
import pandas as pd

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
            input_file = request.files["metadata"]
            input_data = input_file.stream.read().decode("utf-8")
            dataframe = pd.read_csv(StringIO(input_data))

            input_annotation = request.files["annotation"]
            raw_annotation = input_annotation.stream.read().decode("utf-8")
            annotation = pd.read_csv(StringIO(raw_annotation))
            session['first_var'], session['second_var'], session['filtered_num'] = app_functions.make_all_visualisations(dataframe, annotation)

            return redirect(url_for('results'))

    return render_template('home.html',
                           version=__version__)


@app.route("/results", methods=["GET", "POST"])
def results():
    return render_template('results.html',
                           version=__version__,
                           first_var = session['first_var'],
                           second_var = session['second_var'],
                           filtered_num = session['filtered_num'])

@app.route("/data", methods=["GET", "POST"])
def data():
    return render_template('data.html')



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
