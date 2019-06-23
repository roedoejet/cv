from selenium import webdriver
from cv.data import DATA
from cv import __file__ as cv_file
from slugify import slugify
import os

def getScreenshots(DRIVER='/Users/pinea/chromedriver'):
    driver = webdriver.Chrome(DRIVER)
    for project in DATA['projects']:
        if 'links' in project and 'web' in project['links']:
            driver.get(project['links']['web'])
            screenshot = driver.save_screenshot(os.path.join(os.path.dirname(cv_file), 'static/cv/images', slugify(project['title']) + '.png'))
    driver.quit()