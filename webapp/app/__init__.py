from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=False)

app.config['SECRET_KEY'] = 'this-shouldnt-be-here-in-real-app'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' only for db

# db.init_app(app) only for db

#from app.models import Task

from . import views

# from app.views import main as main_blueprint only for blueprints
# app.register_blueprint(main_blueprint)

# with app.app_context(): only for db
#     db.create_all()

