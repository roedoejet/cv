import os
from latex import LatexTemplate
from flask_frozen import Freezer
from cv import app
from fabric.api import local
from screenshot_gen import getScreenshots


def screens():
    getScreenshots()


def latex():
    ltx = LatexTemplate()
    ltx.export()


def freeze():
    root = os.path.dirname(os.path.abspath(__file__))
    docs = os.path.join(root, 'docs')

    # Remove previously generated outputs so stale files don't accumulate.
    # CNAME and any other non-generated files are left untouched.
    local(f'rm -rf {docs}/static {docs}/index.html {docs}/projects')

    # Write directly to docs/ — no intermediate build directory needed.
    app.config['FREEZER_DESTINATION'] = docs
    # Keep CNAME (and any other committed files) that Frozen-Flask didn't generate.
    app.config['FREEZER_REMOVE_EXTRA_FILES'] = False

    freezer = Freezer(app)
    freezer.freeze()
