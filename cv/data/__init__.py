import os
import yaml
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import cv.data as data

DATAPATH = os.path.join(os.path.dirname(data.__file__), "cv.yml")
BIBPATH = os.path.join(os.path.dirname(data.__file__), "publications.bib")

with open(DATAPATH, "r", encoding="utf8") as yml:
    DATA = yaml.safe_load(yml)

# Ensure the template's data.publications reference doesn't crash while the
# template still uses the old data.publications path.  The new canonical
# source is the PUBLICATIONS list built below.
DATA.setdefault("publications", {})


import re as _re

def _strip_braces(s):
    """Remove a single pair of outer curly braces, used for BibTeX name groups."""
    s = s.strip()
    if s.startswith("{") and s.endswith("}"):
        return s[1:-1]
    return s


def _clean_field(s):
    """Strip all BibTeX brace groups from a field value (e.g. {Indigenous} → Indigenous).
    Braces are used in BibTeX to protect capitalisation for LaTeX; they are
    meaningless in an HTML context."""
    return _re.sub(r'\{([^}]*)\}', r'\1', s) if s else s


def _parse_author_str(author_str):
    """Parse a BibTeX 'Last, First and Last, First' author string into dicts."""
    authors = []
    for name in author_str.split(" and "):
        name = name.strip()
        if not name:
            continue
        if "," in name:
            parts = name.split(",", 1)
            last = _strip_braces(parts[0].strip())
            first = _strip_braces(parts[1].strip())
        else:
            last = _strip_braces(name)
            first = ""
        authors.append({"first": first, "last": last})
    return authors


_VENUE_TYPE_BY_ENTRYTYPE = {
    "article": "journal",
    "inproceedings": "proceedings",
    "proceedings": "proceedings",
    "incollection": "book",
    "inbook": "book",
    "book": "book",
    "techreport": "report",
}


_bib_writer = BibTexWriter()
_bib_writer.indent = "  "


def parse_publications(bib_path):
    """Load bib_path and return a list of normalised publication dicts."""
    with open(bib_path, "r", encoding="utf-8") as f:
        bib_db = bibtexparser.load(f)

    results = []
    for entry in bib_db.entries:
        entry_type = entry.get("ENTRYTYPE", "").lower()

        authors = _parse_author_str(entry.get("author", ""))

        if "journal" in entry:
            venue = entry["journal"]
            venue_type = "journal"
        elif "booktitle" in entry:
            venue = entry["booktitle"]
            venue_type = _VENUE_TYPE_BY_ENTRYTYPE.get(entry_type, "proceedings")
        elif "howpublished" in entry:
            venue = entry["howpublished"]
            venue_type = "other"
        else:
            venue = ""
            venue_type = _VENUE_TYPE_BY_ENTRYTYPE.get(entry_type, "other")

        # Entry type always wins for journal / techreport so the mapping is consistent.
        if entry_type in _VENUE_TYPE_BY_ENTRYTYPE:
            venue_type = _VENUE_TYPE_BY_ENTRYTYPE[entry_type]

        def _split_csv(field):
            raw = entry.get(field, "")
            return [v.strip() for v in raw.split(",") if v.strip()] if raw else []

        _mini_db = BibDatabase()
        _mini_db.entries = [entry]
        bibtex_raw = _bib_writer.write(_mini_db).strip()

        results.append(
            {
                "key": entry["ID"],
                "title": _clean_field(entry.get("title", "")),
                "authors": authors,
                "year": int(entry.get("year", 0)),
                "venue": _clean_field(venue),
                "venue_type": venue_type,
                "keywords": _split_csv("keywords"),
                "projects": _split_csv("projects"),
                "featured": entry.get("featured", "").lower() == "true",
                "doi": entry.get("doi") or "",
                "url": entry.get("url") or "",
                "pdf": entry.get("pdf") or "",
                "abstract": entry.get("abstract") or None,
                "bibtex": bibtex_raw,
            }
        )

    return sorted(results, key=lambda p: (-p["year"], p["key"]))


PUBLICATIONS = parse_publications(BIBPATH)

_years = sorted({p["year"] for p in PUBLICATIONS})
print(
    f"[cv.data] Loaded {len(PUBLICATIONS)} publications "
    f"({_years[0]}–{_years[-1]})"
)
