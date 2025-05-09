from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User
import uuid

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']
        # Vérifie unicité du nom d'utilisateur
        if User.query.filter_by(username=username).first():
            flash("Nom d’utilisateur déjà utilisé.", 'danger')
            return redirect(url_for('auth.register'))
        # Création de l'utilisateur
        u = User(username=username, email=email)
        u.set_password(password)
        u.key = uuid.uuid4().hex
        db.session.add(u)
        db.session.commit()
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('shop.index'))
        flash("Nom d’utilisateur ou mot de passe invalide.", 'danger')
        return redirect(url_for('auth.login'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('shop.index'))