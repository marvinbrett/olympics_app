import pytest
import uuid
from app.models import User, Offer
from app import db

def login_admin(client, app):
    # créer admin
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin', email='a@d.min')
        u.set_password('MotDePasseSécurisé')
        u.key = uuid.uuid4().hex
        db.session.add(u); db.session.commit()
    return client.post('/login', data={'username':'admin','password':'MotDePasseSécurisé'}, follow_redirects=True)

def test_admin_offers_and_stats(client, app):
    login_admin(client, app)

    rv = client.get( '/admin/offers' )
    html = rv.get_data( as_text=True )
    assert 'Gérer Offres' in html

    # POST nouvelle offre
    rv = client.post('/admin/offers', data={'name':'Test','price':5,'capacity':2}, follow_redirects=True)
    assert b'Test' in rv.data

    # stats (bar chart)
    rv = client.get('/admin/sales')
    assert rv.status_code == 200
    assert b'chart' in rv.data.lower()