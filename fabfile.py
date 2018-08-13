from latex import LatexTemplate
from flask_frozen import Freezer
from cv import app
from fabric.api import local

def latex():
    ltx = LatexTemplate()
    ltx.export()

def freeze():
    freezer = Freezer(app)
    freezer.freeze()
    local('rm -r docs/static/*')
    local('rm docs/index.html')
    local('cp -r cv/build/* docs/')
