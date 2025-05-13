# tests/conftest.py
import os
import sys
import uuid
import pytest

# ajoute la racine du projet au PYTHONPATH pour que "import app" fonctionne
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from app.models import User

@pytest.fixture
def app():
    # on bascule en mode TESTING, DB en mémoire, CSRF désactivé, et on définit SECRET_KEY
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'tests-secret-key'
    })
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def register(client, username, email, password):
    return client.post('/register',
                       data={'username': username, 'email': email, 'password': password},
                       follow_redirects=True)

def login(client, username, password):
    return client.post('/login',
                       data={'username': username, 'password': password},
                       follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def login_admin(client, app):
    # crée l’admin s’il n’existe pas
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin', email='admin@example.com')
        u.set_password('MotDePasseSécurisé')
        u.key = uuid.uuid4().hex
        db.session.add(u)
        db.session.commit()
    return client.post('/login',
                       data={'username': 'admin', 'password': 'MotDePasseSécurisé'},
                       follow_redirects=True)