from latex import LatexTemplate
from flask_frozen import Freezer
from cv import app

def latex():
    ltx = LatexTemplate()
    ltx.export()

def freeze():
    freezer = Freezer(app)
    freezer.freeze()
