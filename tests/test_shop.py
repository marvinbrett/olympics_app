from app.models import Offer, CartItem
from app import db
import uuid

def test_offers_and_cart_flow(client, app):
    # créer un user
    from app.models import User
    u = User(username='shopper', email='s@h.op')
    u.set_password('Shop1234')
    db.session.add(u)
    db.session.commit()

    # login
    client.post('/login', data={'username':'shopper','password':'Shop1234'}, follow_redirects=True)

    # créer offre
    o = Offer(name='Famille', price=40, capacity=4)
    db.session.add(o); db.session.commit()

    # ajouter au panier via API
    rv = client.post('/add_to_cart', json={'offer_id': o.id})
    assert rv.status_code == 200
    assert rv.get_json()['cart_count'] == 1

    # page /cart contient le nom de l'offre
    rv = client.get('/cart')
    assert b'Famille' in rv.data

    # paiement factice
    rv = client.post('/payment', follow_redirects=True)
    assert b'Veuillez d\u2019abord passer' in rv.data or b'Confirmation de commande' in rv.data

    # historique de commandes
    rv = client.get('/orders')
    assert b'Famille' in rv.data