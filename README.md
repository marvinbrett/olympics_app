# JO France - Billetterie des Jeux Olympiques en France

## 📒 Description

JO France est une application web de billetterie pour les Jeux Olympiques de 2024 en France. Les utilisateurs peuvent :

* Parcourir et acheter des offres de tickets
* Gérer leur panier
* Consulter l'historique de leurs commandes
* Scanner leurs billets (validation ticket)

Les administrateurs peuvent :

* Gérer les offres (CRUD)
* Suivre les ventes et consulter les statistiques
* Gérer les utilisateurs (élever en admin, suppression)

## 🚀 Fonctionnalités

* **Inscription / Connexion** 
* **Rôles** : utilisateur classique et administrateur
* **Catalogue** d'offres de billets (nom, prix, capacité)
* **Panier** : ajout, suppression, validation de commande
* **Historique de commandes**
* **Scan QR code** pour validation (interface `/scan`)
* **Admin Panel** : gestion des offres, ventes, utilisateurs

## 💻 Pré-requis

* Python 3.11+
* PostgreSQL (en production) ou SQLite (en local)
* [Poetry](https://python-poetry.org/) ou `pip`
* Git

## 🔧 Installation locale

```bash
# Cloner le dépôt
git clone https://github.com/marvinbrett/olympics_app.git
cd olympics_app

# Créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🏗️ Configuration

Copiez `.env.example` en `.env` puis configurez :

```ini
FLASK_APP=manage.py
FLASK_ENV=development
SECRET_KEY=UneCléSecrèteTrèsLongue
DATABASE_URL=sqlite:///instance/app.db  # ou PostgreSQL en prod\EMAIL_USER=...
```

## 🚀 Lancement en local

```bash
# Initialiser la base et les migrations
flask db init           # si premiers déploiement
flask db migrate -m "Initial migration"
flask db upgrade

# Lancer le serveur
gunicorn manage:app --bind 0.0.0.0:5000
# ou en dev
flask run
```

## 🔐 Création d’un compte admin

Dans un shell Flask :

```bash
flask shell
>>> from app import db
>>> from app.models import User
>>> u = User(username='admin', email='admin@example.com')
>>> u.set_password('secret')
>>> u.is_admin = True
>>> db.session.add(u)
>>> db.session.commit()
```

## ☁️ Déploiement sur Render

1. Pousser sur GitHub
2. Créer un service Python sur Render
3. Configurer la Build Command :

   ```bash
   pip install -r requirements.txt && flask db upgrade
   ```
4. Configurer la Start Command :

   ```bash
   gunicorn manage:app --bind 0.0.0.0:$PORT
   ```
5. Définir les variables d’environnement dans le dashboard Render

## 📦 Architecture technique

* **Langage** : Python 3.11
* **Framework** : Flask (Blueprints, Jinja2)
* **Extensions** :

  * Flask-Login (authentification)
  * Flask-Migrate (migrations)
  * Flask-SQLAlchemy (ORM)
  * Flask-WTF (forms & CSRF)
* **Base de données** : PostgreSQL (prod) / SQLite (local)
* **Serveur** : Gunicorn
* **Stockage statique** : CDN Render

## 🔒 Sécurité

* **SSL/TLS** via Render
* **Hashing** des mots de passe (Werkzeug)
* **CSRF** protégé par Flask-WTF
* **Contrôle d’accès** : rôles utilisateur / admin
