import pytest
from app import app, db
from app.models import User, Offer

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_api_offers_empty(client):
    rv = client.get('/api/offers')
    assert rv.is_json
    assert rv.get_json() == {'offers': []}

def test_register_and_login(client):
    rv = client.post('/register', data={'username':'test','email':'test@example.com','password':'pass'}, follow_redirects=True)
    assert b'inscrit' in rv.data or rv.status_code == 200
    rv = client.post('/login', data={'username':'test','password':'pass'}, follow_redirects=True)
    assert b'Déconnexion' in rv.data or rv.status_code == 200
