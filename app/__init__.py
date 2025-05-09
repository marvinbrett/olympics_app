from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Création et configuration de l'application
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.config.from_pyfile('config.py', silent=True)

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'auth.login'

# Enregistrement des blueprints
from app.shop.routes import bp as shop_bp
app.register_blueprint(shop_bp)

from app.auth.routes import bp as auth_bp
app.register_blueprint(auth_bp)

from app.admin.routes import bp as admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# Charge les modèles pour être sûr qu'ils sont connus par SQLAlchemy
from app import models
