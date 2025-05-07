import uuid
import io
import base64
import qrcode
from functools import wraps
from flask import (
    render_template, flash, redirect, url_for,
    request, jsonify, session
)
from flask_login import (
    current_user, login_user, logout_user,
    login_required
)
from urllib.parse import urlparse as url_parse

from . import app, db
from .models import User, Offer, Order, CartItem


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            flash('Accès refusé.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    featured = Offer.query.limit(3).all()
    return render_template('index.html', featured=featured)


@app.route('/api/offers')
def api_offers():
    offers = Offer.query.all()
    return jsonify({'offers': [
        {'id': o.id, 'name': o.name, 'price': o.price, 'capacity': o.capacity}
        for o in offers
    ]})


@app.route('/offers')
def offers():
    offers_list = Offer.query.all()
    return render_template('offers.html', offers=offers_list)


@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    offer_id = request.json.get('offer_id')
    ci = CartItem.query.filter_by(
        user_id=current_user.id,
        offer_id=offer_id
    ).first()
    if ci:
        ci.quantity += 1
    else:
        ci = CartItem(user_id=current_user.id, offer_id=offer_id, quantity=1)
        db.session.add(ci)
    db.session.commit()

    total_qty = sum(item.quantity for item in current_user.cart_items)
    return jsonify({'cart_count': total_qty}), 200


@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    offer_id = request.json.get('offer_id')
    ci = CartItem.query.filter_by(
        user_id=current_user.id,
        offer_id=offer_id
    ).first()
    if ci:
        db.session.delete(ci)
        db.session.commit()

    total_qty = sum(item.quantity for item in current_user.cart_items)
    return jsonify({'cart_count': total_qty}), 200


@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Votre panier est vide.', 'info')
        return redirect(url_for('offers'))

    total = sum(ci.quantity * ci.offer.price for ci in cart_items)
    if request.method == 'POST':
        session['paid'] = True
        return redirect(url_for('checkout'))

    return render_template('payment.html', cart_items=cart_items, total=total)


@app.route('/checkout')
@login_required
def checkout():
    if not session.pop('paid', False):
        flash('Veuillez d’abord passer par le paiement.', 'warning')
        return redirect(url_for('payment'))

    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Votre panier est vide.', 'info')
        return redirect(url_for('offers'))

    user = current_user
    group_key = uuid.uuid4().hex
    orders = []

    for ci in items:
        item_key = uuid.uuid4().hex
        order = Order(
            user_id=user.id,
            offer_id=ci.offer.id,
            order_key=item_key,
            final_key=f"{user.key}{item_key}"
        )
        orders.append((order, ci.offer.name))

    db.session.add_all(o for o, _ in orders)
    db.session.commit()

    rendered = []
    for order, name in orders:
        img = qrcode.make(order.final_key)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        data = base64.b64encode(buf.getvalue()).decode('ascii')
        rendered.append({'offer_name': name, 'qr_data': data})

    # vider le panier
    CartItem.query.filter_by(user_id=user.id).delete()
    db.session.commit()

    return render_template(
        'order_confirmation.html',
        orders=rendered,
        order_key=group_key
    )


@app.route('/orders')
@login_required
def order_history():
    # Récupère toutes les commandes de l'utilisateur
    orders = Order.query.filter_by(user_id=current_user.id).all()

    # Pour chaque commande, on reconstruit le QR code en base64
    rendered = []
    for order in orders:
        img = qrcode.make(order.final_key)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_data = base64.b64encode(buf.getvalue()).decode('ascii')
        rendered.append({
            'offer_name': order.offer.name,
            'qr_data': qr_data
        })

    return render_template('orders.html', orders=rendered)


@app.route('/scan', methods=['GET', 'POST'])
def scan():
    result = None
    if request.method == 'POST':
        key = request.form['final_key']
        order = Order.query.filter_by(final_key=key).first()
        result = 'VALID' if order else 'INVALID'
    return render_template('scan.html', result=result)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Nom d'utilisateur déjà utilisé.", 'danger')
            return redirect(url_for('register'))
        user = User(username=username, email=email)
        user.set_password(password)
        user.key = uuid.uuid4().hex
        db.session.add(user)
        db.session.commit()

        flash('Inscription réussie ! Un email de confirmation vous a été envoyé.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Nom d'utilisateur ou mot de passe invalide.", 'danger')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin/offers', methods=['GET', 'POST'])
@admin_required
def admin_offers():
    if request.method == 'POST':
        name = request.form['name']
        price = int(request.form['price'])
        capacity = int(request.form['capacity'])
        db.session.add(Offer(name=name, price=price, capacity=capacity))
        db.session.commit()
        return redirect(url_for('admin_offers'))
    offers = Offer.query.all()
    return render_template('admin_offers.html', offers=offers)


@app.route('/admin/sales')
@admin_required
def admin_sales():
    sales = (
        db.session.query(Offer.name, db.func.count(Order.id))
        .join(Order)
        .group_by(Offer.name)
        .all()
    )
    return render_template('admin_sales.html', sales=sales)


@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username != 'admin':
        db.session.delete(user)
        db.session.commit()
        flash(f"Utilisateur « {user.username} » supprimé.", 'success')
    else:
        flash("Impossible de supprimer l'administrateur principal.", 'warning')
    return redirect(url_for('admin_users'))


@app.context_processor
def inject_cart():
    if current_user.is_authenticated:
        items = current_user.cart_items
        cart_offers = []
        for ci in items:
            for _ in range(ci.quantity):
                cart_offers.append(ci.offer)
        cart_count = sum(ci.quantity for ci in items)
    else:
        cart_offers, cart_count = [], 0
    return dict(cart_offers=cart_offers, cart_count=cart_count)

from .models import Offer
