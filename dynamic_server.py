import json
import gettext

from flask import Flask, render_template, abort

from static_generator import regional_indicator, Translation, PotTranslation, translate_data, locales

app = Flask(__name__)

with open('data.json') as f:
    data = json.load(f)

@app.route("/<lc>")
def locale(lc):
    if lc not in locales:
        abort(404)

    if lc != 'en':
        T = Translation(lc)
    else:
        T = PotTranslation()

    dataT = translate_data(data, T)
    data_json = json.dumps(dataT, separators=(',', ':')).replace("'", "\\'").replace('\\"', '\\\\"') # correct escaping of quotations
    app.jinja_env.install_gettext_translations(T)

    dataT['selected_locale'] = lc
    return render_template('adver.html', data=data_json, **dataT)

@app.route("/")
def hello():
    return locale('en')

if __name__ == "__main__":
    app.jinja_env.add_extension('jinja2.ext.i18n')
    app.jinja_env.install_null_translations()
    app.jinja_env.filters["flag"] = regional_indicator

    data['locales'] = locales
    app.run(debug=True)

