import json

from flask import Flask, render_template

app = Flask(__name__)

with open('data.json') as f:
    data = json.load(f)

@app.route("/")
def hello():
    test = {'a': 'b'}
    return render_template('adver.html', data=json.dumps(data, separators=(',', ':')), **data)

if __name__ == "__main__":
    app.run(debug=True)

