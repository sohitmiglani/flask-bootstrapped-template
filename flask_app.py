# importing general extensions of flask here
from flask import Flask, render_template, request, session, redirect, flash, url_for, make_response, send_file
import flask
from flask_bootstrap import Bootstrap
import app_functions # importing the app_functions.py file to have all the functions ready
from app_functions import __version__
from flask_session import Session


# The code for setting up a user session in flask and securing it with a secret_key is already installed below.
# You can jump directly to building your functions, and collecting HTML inputs for processing.


app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = True
app.config['secret_key'] = app_functions.random_id(50)
app.config['SESSION_TYPE'] = 'filesystem'
sess = Session()
sess.init_app(app)
Bootstrap(app)


@app.route("/", methods=["GET", "POST"])
def home():
    if 'status' not in session:
        # Reset the sessin for you.
        app_functions.reset_session()

    if request.method == "POST":
        if request.form["action"] == "reset":
            # IF the reset button is hit, whole session is reset
            app_functions.reset_session()

        elif request.form["action"] == "action_1":

            # The value of a button in the HTML page must equal 'action_1' for this if loop to be triggered

            file = request.files["file"].read().decode("utf-8")

            # This is how you collect form reponses. 
            # The 'value' attribute of the inputs in HTML must match the string you put in the request.form/
            # So the 'value' attribute of the user id form element must be 'user_id' so that the code below can recognise and receive the input.
            user_id = request.form["user_id"]
            password = request.form['password']
            session['login_data'] = app_functions.log_me_in(user_id,password)
            session['output_data'] = app_functions.process_file(file)

            #Changing the status variable so that the home page gets updated
            session['status'] = 'connected'

        elif request.form["action"] == "action_2":
            # The value of a button in the HTML page must equal 'action_2' for this if loop to be triggered
            # Do something here with the data you collect
            flash('something happened here')

            # These messages will be flashed in the home.html page. 
            # Look at home.html to see where the messages are flashed in the page.
    
        elif request.form["action"] == "action_3":
            flash('This happened.')

            # Do something else here
    
    # Rendering the final template here.
    # We use session variables to store any information and export it back to the HTML page
    # In HTML, you can use these variables by adding the tag {{variable}}
    # For example, if you want to output login_data, just use {{login_data}} in the HTML page

    return render_template('home.html', 
                           status =session['status'],
                           version=__version__,
                           login_data=session['login_data'],
                           output_data=session['output_data'])


# This is another page within the same app that is triggered when you go to the server_url/bug/
@app.route("/bug", methods=["GET", "POST"])
def bug():
    if request.method == "POST":
        if request.form["action"] == "bug_action_1":
            return redirect(url_for("home"))
        elif request.form["action"] == "submit_report":
            flash('something happened here')
            # Do something here with maybe form elements or data you collect in the HTML page

    return render_template('bug_report.html', version=__version__)


# If there is a page that doesn't exist (a 404 error), it redirects you to the home page
@app.errorhandler(404)
def page_not_found(e):
    # the flash utlity flashes a message that can be shown on the main HTML page
    flash('The URL you entered does not exist. You have been redirected to the home page')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
