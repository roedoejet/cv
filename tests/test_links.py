"""Check that links in publications.bib resolve correctly.

Internal PDFs (hosted via GitHub Pages from the local static/ tree) are
checked by verifying the file exists on disk — no network required.

External URLs are parametrized under pytest.mark.slow and only run when
you explicitly opt in:

    uv run pytest -m slow
"""
import os
import pytest
import requests
from cv.data import parse_publications, BIBPATH

_GITHUB_PAGES_PREFIX = '//roedoejet.github.io/cv/static/'
_STATIC_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'cv', 'static')
)


def _classify_links():
    internal, external = [], []
    for p in parse_publications(BIBPATH):
        url = p.get('url') or ''
        if url:
            if _GITHUB_PAGES_PREFIX in url:
                rel = url.split(_GITHUB_PAGES_PREFIX, 1)[1]
                internal.append((p['key'], os.path.join(_STATIC_ROOT, rel)))
            else:
                external.append((p['key'], 'url', url))
        if p.get('doi'):
            external.append((p['key'], 'doi', f"https://doi.org/{p['doi']}"))
    return internal, external


_INTERNAL, _EXTERNAL = _classify_links()


def test_local_pdfs_exist():
    """Every GitHub-Pages-hosted PDF should also exist in cv/static/."""
    missing = [(key, path) for key, path in _INTERNAL if not os.path.exists(path)]
    assert not missing, (
        "Missing local PDF files (present in bib but absent from cv/static/):\n"
        + "\n".join(f"  {key}: {path}" for key, path in missing)
    )


def _normalize(url: str) -> str:
    return 'https:' + url if url.startswith('//') else url


_BROWSER_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# These status codes mean the server is alive and the URL is valid,
# but the server won't serve automated requests. Not a broken link.
_BOT_BLOCKED = {403, 406, 429}


@pytest.mark.slow
@pytest.mark.parametrize(
    "key,field,url",
    _EXTERNAL,
    ids=[f"{k}-{f}" for k, f, _ in _EXTERNAL],
)
def test_external_url_reachable(key, field, url):
    url = _normalize(url)
    try:
        r = requests.head(
            url, allow_redirects=True, timeout=10,
            headers=_BROWSER_HEADERS,
        )
        # Some servers don't support HEAD — retry with GET.
        if r.status_code in (405, 406):
            r = requests.get(
                url, allow_redirects=True, timeout=10, stream=True,
                headers=_BROWSER_HEADERS,
            )
    except requests.exceptions.ConnectionError as exc:
        # TCP-level rejection (bot detection, transient drop) — skip rather
        # than fail; a broken link would give a DNS error or 404, not a reset.
        pytest.skip(f"{url} — connection rejected by server (bot protection?): {exc}")
    except requests.RequestException as exc:
        pytest.fail(f"{url} — {exc}")

    if r.status_code in _BOT_BLOCKED:
        pytest.skip(f"{key} ({field}): {url} returned HTTP {r.status_code} — bot protection, not a dead link")

    assert r.status_code < 400, \
        f"{key} ({field}): {url} returned HTTP {r.status_code}"
