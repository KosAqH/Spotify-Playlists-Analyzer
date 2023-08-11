from . import app
from flask import render_template

# main = Blueprint('main', __name__) only for blueprints

@app.route("/")
def index():
    return render_template('index.html')
