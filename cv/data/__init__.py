import os
import yaml
import cv.data as data

DATAPATH = os.path.join(os.path.dirname(data.__file__), 'cv.yml')

with open(DATAPATH, 'r') as yml:
    DATA = yaml.load(yml)