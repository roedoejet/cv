from cv import app
import os
import cv.data as cv
import yaml
from flask import render_template

@app.route('/')
def home():
    print(cv.DATA)
    return render_template('cv.html', data=cv.DATA)
