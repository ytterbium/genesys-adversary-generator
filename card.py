import json

from flask import Flask, render_template

app = Flask(__name__)

with open('data.json') as f:
    data = json.load(f)

@app.route("/")
def hello():
    return render_template('adver.html', caracteristics=data['caracteristics'], data=json.dumps(data, separators=(',', ':'))
    )

if __name__ == "__main__":
    app.run(debug=True)

