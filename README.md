# Aidan Pine CV
This is the repo that hosts and auto-generates my website as well as my CV. I am using modded Jinja2 to write my LaTeX file as well as my html. Python is running the show with Flask and Flask-Freeze.

If you want to use this for your own CV, edit the data in `cv/cv/data/cv.yml`, and, if necessary, edit the template in `cv/cv/templates/cv.html` and `cv/latex/template.tex`. Then from the root directory, run `fab latex` to generate the cv.latex file, or `fab freeze` to generate a static site.
