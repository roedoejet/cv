from cv import app
import os
import cv.data as cv
import yaml
from flask import render_template

@app.route('/')
def home():
    return render_template('index.html', data=cv.DATA)