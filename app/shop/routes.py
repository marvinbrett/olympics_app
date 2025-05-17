import uuid
import io
import base64
import qrcode
from flask import (
    render_template, flash, redirect, url_for,
    request, jsonify, session, Blueprint
)
from flask_login import current_user, login_required
from sqlalchemy import func
from app import db
from app.models import Offer, Order, CartItem

bp = Blueprint('shop', __name__)

@bp.route('/')
def index():
    # Page d'accueil avec offres mises en avant
    featured = Offer.query.limit(3).all()
    return render_template('index.html', featured=featured)

@bp.route('/api/offers')
def api_offers():
    offers = Offer.query.all()
    return jsonify({'offers': [
        {'id': o.id, 'name': o.name, 'price': o.price, 'capacity': o.capacity}
        for o in offers
    ]})

@bp.route('/offers')
def offers():
    offers_list = Offer.query.all()
    return render_template('offers.html', offers=offers_list)

@bp.route('/add_to_cart', methods=['POST'])
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

@bp.route('/remove_from_cart', methods=['POST'])
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

@bp.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Votre panier est vide.', 'info')
        return redirect(url_for('shop.offers'))

    total = sum(ci.quantity * ci.offer.price for ci in cart_items)
    if request.method == 'POST':
        session['paid'] = True
        return redirect(url_for('shop.checkout'))

    return render_template('payment.html', cart_items=cart_items, total=total)

@bp.route('/checkout')
@login_required
def checkout():
    if not session.pop('paid', False):
        flash('Veuillez d’abord passer par le paiement.', 'warning')
        return redirect(url_for('shop.payment'))

    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Votre panier est vide.', 'info')
        return redirect(url_for('shop.offers'))

    user = current_user
    group_key = uuid.uuid4().hex
    orders = []

    for ci in items:
        item_key = uuid.uuid4().hex
        order = Order(
            user_id=user.id,
            offer_id=ci.offer.id,
            quantity=ci.quantity,
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

@bp.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).all()
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

@bp.route('/scan', methods=['GET', 'POST'])
def scan():
    result = None
    if request.method == 'POST':
        key = request.form['final_key']
        order = Order.query.filter_by(final_key=key).first()
        result = 'VALID' if order else 'INVALID'
    return render_template('scan.html', result=result)

@bp.route('/delete_offer/<int:offer_id>', methods=['POST'])
@login_required
def delete_offer(offer_id):
    if not current_user.is_admin:
        flash("Vous n'avez pas la permission…", "danger")
        return redirect(url_for('shop.offers'))
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    flash(f"L'offre « {offer.name} » a été supprimée.", "success")
    return redirect(url_for('shop.offers'))