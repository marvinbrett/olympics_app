import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config as config_dict  # dict des classes de config
from flask_wtf import CSRFProtect

app = Flask(__name__, instance_relative_config=True)
# Chargement dynamique de la configuration selon FLASK_ENV
env = os.getenv('FLASK_ENV', 'default')
app.config.from_object(config_dict.get(env, config_dict['default']))

# Initialisation des extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Hook : création automatique des tables si nécessaire
@app.before_first_request
def create_tables():
    db.create_all()

login = LoginManager(app)
login.login_view = 'auth.login'

from app.models import User
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

csrf = CSRFProtect(app)

# Enregistrement des blueprints
from app.shop.routes import bp as shop_bp
app.register_blueprint(shop_bp)
csrf.exempt(shop_bp)

from app.auth.routes import bp as auth_bp
app.register_blueprint(auth_bp)

from app.admin.routes import bp as admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

from app import models
