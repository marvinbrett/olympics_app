from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
# from flask_mail import Mail  # décommente si tu utilises Mail

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.config.from_pyfile('config.py', silent=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'auth.login'
# mail = Mail(app)  # si tu utilises l'envoi d'emails

# Enregistre les blueprints après la création du app et db
from app.shop.routes import bp as shop_bp
app.register_blueprint(shop_bp, url_prefix='')

from app.auth.routes import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='')

from app.admin.routes import bp as admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# Importe les modèles pour s'assurer qu'ils sont enregistrés
from app import models