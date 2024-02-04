#!/usr/bin/env python3
import json

from jinja2 import Environment, FileSystemLoader

env = Environment(autoescape=True, loader=FileSystemLoader('./templates/'))

template = env.get_template("adver.html")
with open("data.json", encoding='utf-8') as f:
    data = json.load(f)

data_json = json.dumps(data, separators=(',', ':')).replace("'", "\\'").replace('\\"', '\\\\"') # correct escaping of quotations

with open("adversary.html", 'w', encoding='utf-8') as f:
    f.write(template.render(data=data_json, **data))

