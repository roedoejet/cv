import pytest
from cv.data import parse_publications, BIBPATH
from cv import app as flask_app


@pytest.fixture(scope='session')
def pubs():
    return parse_publications(BIBPATH)


@pytest.fixture(scope='session')
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c
