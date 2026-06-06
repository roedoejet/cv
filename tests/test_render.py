"""Smoke-test Flask routes and verify key content is present in rendered HTML."""
import pytest
from markupsafe import escape as _markup_escape
from cv.data import parse_publications, BIBPATH

THEME_SLUGS = [
    'language-revitalization',
    'speech-technology',
    'digital-lexicography',
    'foundational-lang-tech',
]


@pytest.fixture(scope='module')
def home(client):
    return client.get('/').data.decode()


@pytest.fixture(scope='module')
def projects_page(client):
    return client.get('/projects').data.decode()


def test_home_returns_200(client):
    assert client.get('/').status_code == 200


def test_projects_returns_200(client):
    # Route is /projects/ — Flask 308-redirects the bare /projects, so follow it.
    assert client.get('/projects/', follow_redirects=True).status_code == 200


def test_home_contains_all_theme_slugs(home):
    missing = [slug for slug in THEME_SLUGS if slug not in home]
    assert not missing, f"Theme slug(s) missing from rendered page: {missing}"


def test_home_contains_gantt_elements(home):
    for cls in ('gantt-dot', 'gantt-bar', 'gantt-segment'):
        assert cls in home, f"Expected CSS class '{cls}' not found in rendered page"


def test_all_pub_titles_rendered(home):
    """Every publication title from the bib should appear in the home page HTML.

    Jinja2/MarkupSafe escapes ASCII apostrophes (') to &#39;, so we check both
    the raw title and its MarkupSafe-escaped form.
    """
    pubs = parse_publications(BIBPATH)
    missing = [
        p['title'] for p in pubs
        if p['title'] not in home and str(_markup_escape(p['title'])) not in home
    ]
    assert not missing, (
        "Publication titles missing from rendered page:\n"
        + "\n".join(f"  {t}" for t in missing)
    )
