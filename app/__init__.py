from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from flask_wtf import CSRFProtect


# Création et configuration de l'application
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.config.from_pyfile('config.py', silent=True)

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'auth.login'

from app.models import User
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

csrf = CSRFProtect(app)

from app.shop.routes import bp as shop_bp
app.register_blueprint(shop_bp)
csrf.exempt(shop_bp)

from app.auth.routes import bp as auth_bp
app.register_blueprint(auth_bp)

from app.admin.routes import bp as admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

from app import models
