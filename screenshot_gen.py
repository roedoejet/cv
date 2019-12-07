from selenium import webdriver
from cv.data import DATA
from cv import __file__ as cv_file
from slugify import slugify
import os
from PIL import Image


def getScreenshots(DRIVER='/usr/local/bin/chromedriver', SIZE=(360, 250)):
    driver = webdriver.Chrome(DRIVER)
    driver.set_window_size(1366, 768)
    for project in DATA['projects']:
        if 'links' in project:
            if 'web' in project['links']:
                path = project['links']['web']
            else:
                keys = list(project['links'].keys())
                path = project['links'][keys[0]]
            driver.get(path)
            screen_path = os.path.join(os.path.dirname(
                cv_file), 'static/cv/images', slugify(project['title']) + '.png')
            driver.save_screenshot(screen_path)
            img = Image.open(screen_path)
            img.thumbnail(SIZE)
            img.save(screen_path)
    driver.quit()
