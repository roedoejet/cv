import os
import re
import yaml
import requests
from unittest import TestCase
from test_log import LOGGER

class URLsTest(TestCase):
    def setUp(self):
        with open(os.path.join('../cv/data', 'cv.yml')) as f:
            self.data = yaml.safe_load(f)

    def test_urls(self):
        url_regex = r'[http]*[s]?:?//[\w\.\d\/\-\?\=\&\%]+'
        urls = re.findall(url_regex, str(self.data))
        for url in urls:
            if not url.startswith('http'):
                url = 'https:' + url
            req = requests.get(url)
            LOGGER.info(f'Pinging {url}')
            self.assertEqual(req.status_code, 200)