# Aidan Pine CV
This is the repo that hosts and auto-generates my website as well as my CV. I am using modded Jinja2 to write my LaTeX file as well as my html. Python is running the show with Flask and Flask-Freeze.

If you want to use this for your own CV, edit the data in `cv/data/cv.yml` (résumé content lives under `resume:`) and `cv/data/publications.bib`, and, if necessary, edit the templates in `cv/templates/` and `latex/resume_template.tex`. Then from the root directory, run `uv run fab resume` to build the PDF résumé (requires `xelatex` and the New Computer Modern font, both in TeX Live), or `uv run fab freeze` to generate a static site.
