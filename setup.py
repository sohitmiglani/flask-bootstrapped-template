from setuptools import setup
from setuptools.command.install import install
from io import open


install_requires = ['flask','flask_session','flask_bootstrap','urllib3','twisted']

setup(
    name='flask-bootstrap-template',
    version='1.0.1',
    author='Sohit Miglani',
    author_email='sohitmiglani@gmail.com',
    description='Template for building Flask apps at NIBR',
    license='MIT',
    install_requires=install_requires,
    py_modules=['flask_app'],
    classifiers=[
            "License :: MIT",
            "Environment :: Console",
            "Intended Audience :: Science/Research",
            "Natural Language :: English",
            "Operating System :: Unix",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.6",
            "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
