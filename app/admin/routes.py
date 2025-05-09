# app/admin/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Offer, Order, User
from sqlalchemy import func
import json
from . import bp
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            flash('Accès refusé.', 'warning')
            return redirect(url_for('shop.index'))
        return f(*args, **kwargs)
    return decorated


@bp.route('/offers', methods=['GET', 'POST'])
@admin_required
def admin_offers():
    if request.method == 'POST':
        name = request.form.get('name')
        price = int(request.form.get('price', 0))
        capacity = int(request.form.get('capacity', 0))
        db.session.add(Offer(name=name, price=price, capacity=capacity))
        db.session.commit()
        return redirect(url_for('admin.admin_offers'))
    offers = Offer.query.all()
    return render_template('admin_offers.html', offers=offers)


@bp.route('/sales')
@admin_required
def admin_sales():
    sales = (
        db.session
          .query(Offer.name, func.sum(Order.quantity).label('places_vendues'))
          .join(Order)
          .group_by(Offer.name)
          .all()
    )
    labels = [name for name, _ in sales]
    data = [int(count or 0) for _, count in sales]
    return render_template(
        'admin_sales.html',
        labels=json.dumps(labels),
        data=json.dumps(data)
    )


@bp.route('/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username != 'admin':
        db.session.delete(user)
        db.session.commit()
        flash(f"Utilisateur « {user.username} » supprimé.", 'success')
    else:
        flash("Impossible de supprimer l'administrateur principal.", 'warning')
    return redirect(url_for('admin.admin_users'))
