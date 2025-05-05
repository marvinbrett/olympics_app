# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config.Config')

# extensions
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models