import os
from latex import ResumeTemplate
from flask_frozen import Freezer
from cv import app
from fabric.api import local
from screenshot_gen import getScreenshots


def screens():
    getScreenshots()


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


def resume():
    """Render latex/resume.tex from cv.yml + publications.bib, compile it with
    xelatex, and publish the PDF as the site's downloadable CV."""
    tex = ResumeTemplate().export()
    latex_dir = os.path.dirname(tex)
    local(f'cd {latex_dir} && xelatex -interaction=nonstopmode -halt-on-error resume.tex')
    root = os.path.dirname(os.path.abspath(__file__))
    local(f'cp {latex_dir}/resume.pdf {root}/cv/static/cv/pdfs/cv-gen.pdf')
