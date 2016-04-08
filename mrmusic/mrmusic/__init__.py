"""
The flask application package.
"""
from __future__ import print_function
from flask import Flask
app = Flask(__name__)
app.config.from_object('config')
import mrmusic.views
