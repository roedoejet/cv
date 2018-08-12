from latex import LatexTemplate
from flask_frozen import Freezer
from cv import app

def latex():
    ltx = LatexTemplate()
    ltx.export()

def freeze():
    app.config['FREEZER_BASE_URL'] = 'https://roedoejet.github.io/cv-flask/cv/build/'
    freezer = Freezer(app)
    freezer.freeze()
