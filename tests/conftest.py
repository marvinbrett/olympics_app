import os
import sys
import uuid
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from app.models import User

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'tests-secret-key'
    })
    with flask_app.app_context():
        db.create_all()

        # --- créer un utilisateur "standard" pour id=1 (FK tests) ---
        user = User(username='user1', email='user1@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        yield flask_app

        # cleanup
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def register(client, username, email, password):
    return client.post(
        '/register',
        data={'username': username, 'email': email, 'password': password},
        follow_redirects=True
    )

def login(client, username, password):
    return client.post(
        '/login',
        data={'username': username, 'password': password},
        follow_redirects=True
    )

def logout(client):
    return client.get('/logout', follow_redirects=True)

def login_admin(client, app):
    """
    Crée un admin (si nécessaire) et renvoie la réponse du POST /login
    Tests d’admin attendent le password 'MotDePasseSécurisé'
    """
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com')
        admin.is_admin = True
        admin.set_password('MotDePasseSécurisé')
        admin.key = uuid.uuid4().hex
        db.session.add(admin)
        db.session.commit()

    return client.post(
        '/login',
        data={'username': 'admin', 'password': 'MotDePasseSécurisé'},
        follow_redirects=True
    )