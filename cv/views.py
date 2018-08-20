from cv import app
import os
import cv.data as cv
import yaml
from flask import render_template

# Change around the structure to make it easier for template
pubs = cv.DATA['publications']
pub_years = set([p['year'] for p in pubs])
new_pubs = {y: [p for p in pubs if p['year'] == y] for y in pub_years}
cv.DATA['publications'] = new_pubs

@app.route('/')
def home():
    return render_template('cv.html', data=cv.DATA)
