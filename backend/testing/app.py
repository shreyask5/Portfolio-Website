from flask import Flask
app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to Home page"

@app.route("/search")
def search():
    return "Welcome to Search page"

@app.route("/mail")
def mail():
    return "Welcome to mail page"
app.run();
