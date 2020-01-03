import json

from flask import Flask, render_template

app = Flask(__name__)

with open('data.json') as f:
    data = json.load(f)

@app.route("/")
def hello():
    test = {'a': 'b'}
    print(data['defense'], 'r')
    data_json = json.dumps(data, separators=(',', ':')).replace("'", "\\'").replace('\\"', '\\\\"') # correct escaping of quotations
    return render_template('adver.html', data=data_json, **data)

if __name__ == "__main__":
    app.run(debug=True)

