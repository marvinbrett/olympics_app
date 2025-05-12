import uuid
import pytest
from app.models import User, Offer, CartItem, Order
from app import db

def test_user_password_hashing(app):
    u = User(username='alice', email='a@b.c')
    u.set_password('Secret123')
    assert u.check_password('Secret123')
    assert not u.check_password('Wrong')

def test_offer_and_order_relationship(app):
    o = Offer(name='Solo', price=10, capacity=5)
    db.session.add(o)
    db.session.commit()

    # créer commande
    order = Order(user_id=1, offer_id=o.id, quantity=2,
                  order_key=uuid.uuid4().hex,
                  final_key=uuid.uuid4().hex)
    db.session.add(order)
    db.session.commit()

    # relation backref
    assert order in o.orders
    assert o.orders[0].quantity == 2

def test_cart_item(app):
    # créer user et offre
    u = User(username='bob', email='b@c.d')
    u.set_password('Pwd12345')
    db.session.add(u)
    o = Offer(name='Duo', price=20, capacity=10)
    db.session.add(o)
    db.session.commit()

    # ajouter au panier
    ci = CartItem(user_id=u.id, offer_id=o.id, quantity=3)
    db.session.add(ci)
    db.session.commit()

    assert ci.offer.name == 'Duo'
    assert ci.user.username == 'bob'
    assert ci.quantity == 3