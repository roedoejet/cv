import os
import re
import yaml
import requests
from unittest import TestCase
from test_log import LOGGER

class URLsTest(TestCase):
    """Test for dead links"""
    def setUp(self):
        with open(os.path.join('../cv/data', 'cv.yml')) as f:
            self.data = yaml.safe_load(f)

    def test_urls(self):
        url_regex = r'[http]*[s]?:?//[\w\.\d\/\-\?\=\&\%]+'
        urls = re.findall(url_regex, str(self.data))
        URLS_FAILED = 0
        for url in urls:
            if not url.startswith('http'):
                url = f'https:{url}'
            req = requests.get(url)
            LOGGER.info(f'Pinging {url}')
            try:
                self.assertEqual(req.status_code, 200)
            except AssertionError:
                URLS_FAILED += 1
                LOGGER.warn(f"url {url} returned status {req.status_code}")
        self.assertEqual(URLS_FAILED, 0)