from flask import Flask
import hashlib
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

def _static_hash(filename):
    """Return an 8-char MD5 of a static file for cache-busting."""
    path = os.path.join(app.static_folder, filename)
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except OSError:
        return '0'

@app.context_processor
def inject_asset_versions():
    return {
        'css_v': _static_hash('cv/dist/css/custom.css'),
        'js_v':  _static_hash('cv/dist/js/main.js'),
    }

import cv.views