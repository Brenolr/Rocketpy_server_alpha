from flask import Flask

app = Flask(__name__)

@app.route("/kenobi")
def home_view():
    return"<h1>Hello There<h1>"