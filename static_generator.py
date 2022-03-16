#!/usr/bin/env python3
import json
import gettext

from jinja2 import Environment, FileSystemLoader

localedir = 'locale'
domain = 'genesys'

locales = ['fr', 'pl']

class Translation(gettext.GNUTranslations):
    def __init__(self, fp=None):
        self.pot = {}

        super().__init__(fp)

    def translate(self, message, context=None):
        self.pot[self.sanitize_message(message)] = context

        if hasattr(self, '_catalog'):
            return self.gettext(message)
        else:
            return message

    _ = translate

    def write_pot(self, fp=None):
        pot_list = []
        for msg, context in self.pot.items():
            pot_list.append('')
            if context:
                pot_list.append("#: " + context)
            pot_list.append(f'msgid "{msg}"')
            pot_list.append('msgstr ""')

        pot_str = '\n'.join(pot_list)

        if fp:
            fp.write(pot_str)
        else:
            return pot_str

    def sanitize_message(self, msg):
        return msg.replace('"', r'\"')
    

def translate_data(data, T):
    for c in data['caracteristics']:
        c['name'] = T.translate(c["name"], "caracteristics")
        c['ex'] = T.translate(c["ex"], f"examples {c['name']}")

    for s in data['skills']:
        s['name'] = T.translate(s['name'], 'skills')

    for t in data['talents']:
        t['talent'] = T.translate(t['talent'], 'talents')
        t['desc'] = T.translate(t['desc'], f'description {t["talent"]}')

    for a in data['abilities']:
        a['ability'] = T.translate(a['ability'], 'abilities')
        a['ex'] = T.translate(a["ex"], f"examples {a['ability']}")
        a['desc'] = T.translate(a['desc'], f'description {a["ability"]}')

    for e in data['equipment']:
        e['name'] = T.translate(e["name"], "equipments")
        e['desc'] = T.translate(e['desc'], f'description {e["name"]}')
        e['weapons'] = T.translate(e['weapons'], f'weapons {e["name"]}')
        e['equipment'] = T.translate(e['equipment'], f'equipment {e["name"]}')

    for d in data['defense']:
        d['name'] = T.translate(d["name"], "defenses")
        d['ex'] = T.translate(d["ex"], f"examples {d['name']}")



if __name__ == "__main__":
    with open("data.json") as f:
        data = json.load(f)

    env = Environment(autoescape=True, loader=FileSystemLoader('./templates/'))
    template = env.get_template("adver.html")

    for lc in locale:
        # Create the locale folder
        T = Translation(lc)
        
        T = gettext.translation('messages', localedir=localedir, languages='fr', class_=Translation)
    try:
        print('found')
    except FileNotFoundError:
        T = Translation(None)
    
    translate_data(data, T)

    with open(f'{localedir}/{domain}.pot', 'w') as f:
        T.write_pot(f)

    data_json = json.dumps(data, separators=(',', ':')).replace("'", "\\'").replace('\\"', '\\\\"') # correct escaping of quotations

    with open("adversary.html", 'w') as f:
        f.write(template.render(data=data_json, **data))

