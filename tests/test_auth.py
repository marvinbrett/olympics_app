import uuid
from app.models import User
from app import db

def register(client, username, email, password):
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def test_register_and_login_logout(client, app):
    # inscription
    rv = register( client, 'testu', 't@e.st', 'Mypass123' )
    html = rv.get_data( as_text=True )
    assert 'Inscription réussie' in html

    # connexion
    rv = login( client, 'testu', 'Mypass123' )
    html = rv.get_data( as_text=True )
    assert 'Mes commandes' in html  # redirigé vers shop.index

    # déconnexion
    rv = client.get( '/logout', follow_redirects=True )
    html = rv.get_data( as_text=True )
    assert 'Connexion' in html