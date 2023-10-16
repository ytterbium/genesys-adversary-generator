#!/usr/bin/env python3
import copy
from datetime import datetime
import gettext
import json
from pathlib import Path
import subprocess
import unicodedata

from jinja2 import Environment, FileSystemLoader

localedir = 'locale'
domain = 'genesys'

locales = ['en', 'fr', 'pl']

pot_header = '''\
# Translation for the genesys adversary generator
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"POT-Creation-Date: {time}\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
'''

class Translation(gettext.GNUTranslations):
    pot_file = Path('.') / localedir / (domain + '.pot')

    def __init__(self, locale):
        self.locale_dir = Path('.') / localedir / locale

        self.locale_dir.mkdir(parents=True, exist_ok=True) # ensure the directory specific to the locale exist

        po_file = self.locale_dir / (domain + '.po') 
        mo_file = self.locale_dir / (domain + '.mo')

        # generate all po and mo files if the pot already exits
        if self.pot_file.exists():
            if not po_file.exists():
                # initialize po file
                subprocess.run(['msginit', '-i', str(self.pot_file), '-o', str(po_file), '-l', locale])
            else:
                # update po file
                subprocess.run(['msgmerge', str(po_file), str(self.pot_file), '-U'])

            subprocess.run(['msgfmt', '-o', str(mo_file), str(po_file)])

            with open(mo_file, 'rb') as fp:
                super().__init__(fp)

    def gettext(self, message, context=None):
        return super().gettext(message)

    ngettext = gettext


class PotTranslation:
    """
    Class with no translation (keep the english).
    Useful to generate the pot file
    """
    pot_file = Path('.') / localedir / (domain + '.pot')

    def __init__(self):
        self.pot = {}


    def gettext(self, message, context=None):
        s_message = self.sanitize_message(message)
        if s_message not in self.pot:
            self.pot[s_message] = context

        return message

    ngettext = gettext

    def write_pot(self, fp=None):
        pot_list = [pot_header.format(time=datetime.utcnow().isoformat())]
        for msg, context in self.pot.items():
            pot_list.append('')
            if context:
                pot_list.append("#: " + context)
            pot_list.append(f'msgid "{msg}"')
            pot_list.append('msgstr ""')

        pot_str = '\n'.join(pot_list)

        with self.pot_file.open('w') as f:
            f.write(pot_str)

        return pot_str

    def sanitize_message(self, msg):
        return msg.replace('"', r'\"')

def regional_indicator(string):
    """Unicode chars of flag"""

    if string == 'en':
        return regional_indicator('gb')

    r = ""
    for char in string:
        r += unicodedata.lookup(f"REGIONAL INDICATOR SYMBOL LETTER {char}")

    return r


    

def translate_data(data, T):
    data = copy.deepcopy(data)
    for c in data['caracteristics']:
        c['name'] = T.gettext(c["name"], "caracteristics")
        c['ex'] = T.gettext(c["ex"], f"examples {c['name']}")
        c['caracs'] = {carac: [T.gettext(carac, "caracteristics"), nb]
                       for carac, nb in c['caracs'].items()}

    for s in data['skills']:
        s['name'] = T.gettext(s['name'], 'skills')
        #s['skills'] = {carac: [T.gettext(carac, "skill name"), nb] for carac, nb in s['skills'].items()}
        s['skills'] = {T.gettext(carac, "skill name"): nb for carac, nb in s['skills'].items()}

    for t in data['talents']:
        t['talent'] = T.gettext(t['talent'], 'talents')
        t['desc'] = T.gettext(t['desc'], f'description {t["talent"]}')

    for a in data['abilities']:
        a['ability'] = T.gettext(a['ability'], 'abilities')
        a['ex'] = T.gettext(a["ex"], f"examples {a['ability']}")
        a['desc'] = T.gettext(a['desc'], f'description {a["ability"]}')

    for e in data['equipment']:
        e['name'] = T.gettext(e["name"], "equipments")
        e['desc'] = T.gettext(e['desc'], f'description {e["name"]}')
        e['weapons'] = T.gettext(e['weapons'], f'weapons {e["name"]}')
        e['equipment'] = T.gettext(e['equipment'], f'equipment {e["name"]}')

    for d in data['defense']:
        d['name'] = T.gettext(d["name"], "defenses")
        d['ex'] = T.gettext(d["ex"], f"examples {d['name']}")
        d['defense'] = {carac: [T.gettext(carac, "defense caracteristic"), nb]
                       for carac, nb in d['defense'].items()}

    return data

def write_template(template, data, locale=None):
    data_json = json.dumps(data, separators=(',', ':')).replace("'", "\\'").replace('\\"', '\\\\"') # correct escaping of quotations
    
    if locale:
        file_name = f"{locale}.html"
    else:
       file_name = "en.html"

    with open(file_name, "w") as f:
        f.write(template.render(data=data_json, **data))

if __name__ == "__main__":
    with open("data.json") as f:
        data = json.load(f)

    data['locales'] = locales

    env = Environment(autoescape=True, loader=FileSystemLoader('./templates/'), extensions=['jinja2.ext.i18n'])
    env.filters['flag'] = regional_indicator
    
    # Pot extraction and generation of english template
    nT = PotTranslation()
    for f in ['adver.html', 'wt.svg', 'st.svg', 'soak.svg', 'defense.svg']:
        for m in env.extract_translations(env.loader.get_source(env, f)[0]):
            nT.gettext(m[2], f"template L {m[0]}")


    data['selected_locale'] = 'en'
    data_pot = translate_data(data, nT)
    nT.write_pot()

    env.install_null_translations()
    template = env.get_template("adver.html")
    write_template(template, data_pot)

    # Generation of translated templates
    for lc in locales:
        if lc != 'en':
            # Create the locale folder
            T = Translation(lc)
            
            dataT = translate_data(data, T)
            dataT['selected_locale'] = lc
            env.install_gettext_translations(T)
            template = env.get_template("adver.html")

            write_template(template, dataT, lc)

