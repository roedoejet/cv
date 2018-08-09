import os
import jinja2
import re
import latex as lt
import cv.data as cv

def sanitize(data):
    data = re.sub(r'(?<=[^\\])%', r'\\%', data)
    return data

def initial(data):
    return data[0]

def alph(n):
    return chr(96 + n)


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
        self.latexJinjaEnv.filters['sanitize'] = sanitize
        self.latexJinjaEnv.filters['initial'] = initial
        self.latexJinjaEnv.filters['alph'] = alph
        self.template = self.latexJinjaEnv.get_template('template.tex')
        
        self.data = cv.DATA
        
    def export(self):
        with open(os.path.join(self.dir, 'cv.tex'), 'w', encoding='utf8') as f:
            f.write(self.template.render(data=self.data))