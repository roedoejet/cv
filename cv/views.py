from cv import app
import cv.data as cv
from flask import render_template


@app.route('/')
def home():
    return render_template('cv.html', data=cv.DATA, publications=cv.PUBLICATIONS)


@app.route('/projects/')
def projects():
    return render_template('projects.html', data=cv.DATA, publications=cv.PUBLICATIONS)
