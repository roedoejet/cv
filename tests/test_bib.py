"""Validate the structure and content of publications.bib."""
import bibtexparser
import pytest
from cv.data import BIBPATH

KNOWN_SLUGS = frozenset({
    'language-revitalization',
    'speech-technology',
    'digital-lexicography',
    'foundational-lang-tech',
})


@pytest.fixture(scope='module')
def raw_db():
    with open(BIBPATH) as f:
        return bibtexparser.load(f)


def test_no_duplicate_keys(raw_db):
    keys = [e['ID'] for e in raw_db.entries]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    assert not dupes, f"Duplicate BibTeX keys: {dupes}"


def test_required_fields(pubs):
    errors = []
    for p in pubs:
        if not p['title']:   errors.append(f"{p['key']}: empty title")
        if not p['year']:    errors.append(f"{p['key']}: missing year")
        if not p['authors']: errors.append(f"{p['key']}: no authors")
    assert not errors, "\n".join(errors)


def test_year_in_range(pubs):
    bad = [f"{p['key']}: {p['year']}" for p in pubs if not 2000 <= p['year'] <= 2030]
    assert not bad, "Years outside 2000–2030:\n" + "\n".join(bad)


def test_every_pub_has_at_least_one_keyword(pubs):
    missing = [p['key'] for p in pubs if not p['keywords']]
    assert not missing, f"Publications with no keywords (must belong to at least one theme): {missing}"


def test_all_keywords_are_known_slugs(pubs):
    errors = [
        f"{p['key']}: {set(p['keywords']) - KNOWN_SLUGS}"
        for p in pubs if set(p['keywords']) - KNOWN_SLUGS
    ]
    assert not errors, "Unknown keyword slugs:\n" + "\n".join(errors)


def test_doi_is_identifier_not_url(raw_db):
    """doi field should hold only the DOI identifier (e.g. 10.18/...), not a full URL."""
    bad = [
        f"{e['ID']}: {e['doi']!r}"
        for e in raw_db.entries
        if e.get('doi', '').strip().startswith('http')
    ]
    assert not bad, "doi fields contain full URLs instead of bare identifiers:\n" + "\n".join(bad)
