from flask import Flask

app = Flask(__name__, instance_relative_config=False)

# app.config['SECRET_KEY'] = 'this-shouldnt-be-here-in-real-app'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' only for db

from . import views

