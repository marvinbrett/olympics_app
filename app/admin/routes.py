from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Offer, Order
from app.models import User
from app.forms import OfferForm
from app.forms import EmptyForm
from flask import abort

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @login_required
    def decorated_view(*args, **kwargs):
        if current_user.username != 'admin':
            flash('Accès refusé.', 'danger')
            return redirect(url_for('shop.index'))
        return f(*args, **kwargs)
    decorated_view.__name__ = f.__name__
    return decorated_view

@bp.route('/offers', methods=['GET', 'POST'])
@admin_required
def admin_offers():
    form = OfferForm()
    if form.validate_on_submit():
        # Convertit le prix en float pour compatibilité SQLite
        price = float(form.price.data)
        o = Offer(name=form.name.data,
                  price = price,
                  capacity = form.capacity.data)
        db.session.add(o)
        db.session.commit()
        flash('Offre ajoutée avec succès.', 'success')
        return redirect(url_for('admin.admin_offers'))
    offers = Offer.query.all()
    return render_template('admin_offers.html', offers=offers, form=form)

@bp.route('/sales')
@admin_required
def admin_sales():
    sales = (
        db.session.query(
            Offer.name,
            db.func.sum( Order.quantity ).label( 'tickets_sold' )
        )
        .join(Order)
        .group_by( Offer.id )
        .all()
    )

    labels = [name for name, count in sales]
    data = [count for name, count in sales]
    return render_template(
        'admin_sales.html',
        sales=sales,
        labels = labels,
        data = data
    )

@bp.route('/users')
@admin_required
def admin_users():
    users = User.query.order_by( User.id ).all()
    delete_form = EmptyForm()
    return render_template('admin_users.html',
                           users=users,
    delete_form = delete_form)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    form = EmptyForm()
    if not form.validate_on_submit():
        abort( 400 )
    user = User.query.get_or_404( user_id )
    if user.username == 'admin':
        flash( "Vous ne pouvez pas supprimer l’utilisateur ‘admin’.", 'warning' )
    else:
        db.session.delete( user )
        db.session.commit()
        flash( f"Utilisateur {user.username} supprimé.", 'success' )
    return redirect( url_for( 'admin.admin_users' ) )