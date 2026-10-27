import os
import jinja2
import re
import latex as lt
import cv.data as cv

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

def tex(value):
    """Escape a data value for LaTeX. Unicode is left as-is for xelatex."""
    if isinstance(value, str):
        return sanitize(value)
    return value


def format_authors(authors, me, max_authors):
    """Format authors as 'Last, F.', bolding `me` and truncating with 'et al.'"""
    names = []
    for a in authors[:max_authors]:
        name = a['last']
        if a['first']:
            name += ', {}.'.format(a['first'].lstrip('{\\\'`^"~=.')[0])
        if a['last'] == me['last_name'] and a['first'].startswith(me['first_name']):
            name = '\\textbf{{{}}}'.format(name)
        names.append(name)
    if len(authors) > max_authors:
        names.append('et al.')
    return ', '.join(names)


def resume_publications(resume, personal, publications):
    """Resolve résumé publication entries against the parsed bib.

    Returns dicts with formatted authors, newest first.
    """
    by_key = {p['key']: p for p in publications}
    missing = [e['key'] for e in resume['publications'] if e['key'] not in by_key]
    if missing:
        raise KeyError('Résumé publications not found in publications.bib: {}'.format(', '.join(missing)))

    max_authors = resume.get('max_authors', 9)
    pubs = []
    for entry in resume['publications']:
        p = by_key[entry['key']]
        pubs.append({
            'authors': format_authors(p['authors'], personal, max_authors),
            'title': p['title'],
            'venue': entry.get('venue', p['venue']),
            'venue_type': p['venue_type'],
            'address': p['address'],
            'publisher': p['publisher'],
            'note': entry.get('note', ''),
            'year': p['year'],
        })
    # Stable sort keeps the YAML order within a year.
    pubs.sort(key=lambda p: -p['year'])
    return pubs


def latest_year(year):
    """Latest four-digit year in free text like '2014, 2015 & 2016' or '2015–2024'."""
    return max(int(y) for y in re.findall(r'\d{4}', str(year)))


def newest_first(entries):
    """Sort entries on the latest year in their `year` field; ties keep their order."""
    return sorted(entries, key=lambda e: -latest_year(e['year']))


def awards_and_grants(data):
    """Merge `awards` and `grants` into one list, newest first."""
    entries = []
    for e in data.get('awards', []) + data.get('grants', []):
        title = e['title']
        if e.get('amount'):
            title += ' ({})'.format(str(e['amount']).replace('$', '\\$'))
        entries.append({'title': title, 'project': e.get('project', ''), 'year': str(e['year'])})
    return newest_first(entries)


class ResumeTemplate():
    """Renders latex/resume_template.tex from the `resume` section of cv.yml.

    Values are escaped individually (via finalize) so the template itself can
    use & and % freely.
    """
    def __init__(self):
        self.dir = os.path.dirname(lt.__file__)
        self.latexJinjaEnv = jinja2.Environment(
            block_start_string='\\jblock{',
            block_end_string='}',
            variable_start_string='\\jvar{',
            variable_end_string='}',
            comment_start_string='\\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
            finalize=tex,
            loader=jinja2.FileSystemLoader(self.dir)
        )
        self.template = self.latexJinjaEnv.get_template('resume_template.tex')

        self.data = cv.DATA

    def export(self):
        resume = self.data['resume']
        publications = resume_publications(resume, self.data['personal'], cv.PUBLICATIONS)
        path = os.path.join(self.dir, 'resume.tex')
        with open(path, 'w', encoding='utf8') as f:
            f.write(self.template.render(data=self.data, resume=resume, publications=publications,
                                         awards=awards_and_grants(self.data),
                                         teaching=newest_first(resume['teaching'])))
        return path