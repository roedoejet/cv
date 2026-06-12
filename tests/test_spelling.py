"""Spell-check authored prose using codespell.

codespell checks against a curated dictionary of ~10 000 known typos rather
than a general English dictionary, so false-positive rates on technical
content are very low.  Domain-specific terms that it incorrectly flags can
be added to [tool.codespell] ignore-words-list in pyproject.toml.

Run with:  uv run pytest tests/test_spelling.py -v
"""
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent

_PATHS = [
    "cv/templates",
    "cv/data/cv.yml",
    "cv/data/publications.bib",
]


def test_no_spelling_errors():
    # Resolve the codespell binary from the same venv as the running interpreter.
    codespell = Path(sys.executable).parent / "codespell"
    result = subprocess.run(
        [str(codespell), "--toml", "pyproject.toml", *_PATHS],
        capture_output=True,
        text=True,
        cwd=_ROOT,
    )
    assert result.returncode == 0, (
        "codespell found spelling errors — fix them or add to "
        "[tool.codespell] ignore-words-list in pyproject.toml:\n\n"
        + result.stdout
    )
