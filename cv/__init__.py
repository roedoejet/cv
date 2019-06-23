from flask import Flask
import os
from slugify import slugify

VERSION = '1.0'

class Config(object):
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get("PORT", 5500))
    THREADED = True
    HEROKU = False

app = Flask(__name__)

@app.template_filter('initial')
def initial(data):
        return data[0]

@app.template_filter('alph')
def alph(n):
      return chr(96 + n)

@app.template_filter('slug')
def slug(s):
    return slugify(s)

import cv.views