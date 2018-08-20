import os
import jinja2
import re
import latex as lt
import cv.data as cv
from pylatexenc.latexencode import utf8tolatex
from calendar import month_abbr

def sanitize(data):
    escape_characters = ''.join(["%", "&"])
    findall_pattern = re.compile(r'(?<=[^\\])[{}]'.format(escape_characters))
    try:
        matches = findall_pattern.findall(data)
        replaced_data = data
        for match in matches:
            find_pattern = r'(?<=[^\\]){}'.format(match)
            replace_pattern = r'\\{}'.format(match)
            replaced_data = re.sub(find_pattern, replace_pattern, replaced_data)
        return replaced_data
    except AttributeError:
        return data
    return data

def initial(data):
    return data[0]

def alph(n):
    return chr(96 + n)

def month(n):
    return month_abbr[n]


class LatexTemplate():
    def __init__(self):
        self.dir = os.path.dirname(lt.__file__)
        self.latexJinjaEnv = jinja2.Environment(
            block_start_string='\jblock{',
            block_end_string='}',
            variable_start_string='\jvar{',
            variable_end_string='}',
            comment_start_string='\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
            loader=jinja2.FileSystemLoader(self.dir)
            
        )
        self.latexJinjaEnv.filters['initial'] = initial
        self.latexJinjaEnv.filters['alph'] = alph
        self.latexJinjaEnv.filters['month'] = month
        self.template = self.latexJinjaEnv.get_template('template.tex')
        
        self.data = cv.DATA
        
    def export(self):
        with open(os.path.join(self.dir, 'cv.tex'), 'w', encoding='utf8') as f:
            f.write(utf8tolatex(sanitize(self.template.render(data=self.data)), non_ascii_only=True))