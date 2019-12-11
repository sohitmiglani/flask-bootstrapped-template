# This .py file houses all the major functions you'll use in your flask app.
# Have all the functions here and then import them in the flask_app.py file.

import pandas # import all the required libraries here
import random

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


def log_me_in(userid, password):
    # Do something with userid and password
    data = 'You are logged in'
    return data

def process_file(file):
    # Take the file and do something with it
    return 'This is the content of the file you uploaded'
