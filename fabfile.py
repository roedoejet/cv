from latex import LatexTemplate
from flask_frozen import Freezer
from cv import app
from fabric.api import local

def latex():
    ltx = LatexTemplate()
    ltx.export()

def freeze():
    app.config['FREEZER_BASE_URL'] = 'https://roedoejet.github.io/cv-flask/'
    freezer = Freezer(app)
    freezer.freeze()
    local('rm -r docs/*')
    local('cp -r cv/build/* docs/')
