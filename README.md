# JO France - Billetterie Jeux Olympiques

Ce projet est une application Flask de billetterie pour les Jeux Olympiques en France.

## 1. Prérequis

- Python 3.9+
- [pipenv](https://pipenv.pypa.io/) ou `venv`
- SQLite (par défaut) ou une autre base via `DATABASE_URL`

## 2. Installation

```bash
# Cloner le dépôt
git clone https://github.com/marvinbrett/olympics_app.git
cd olympics_app

# Créer l'environnement virtuel et installer les dépendances
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Créer le fichier .env à partir du modèle
cp .env.example .env
# Éditez .env pour définir vos clés et URI

# Initialiser la base de données
export FLASK_APP=manage.py
flask db upgrade
```

## 3. Scripts CLI

### `flask create-admin`

Permet de créer un compte administrateur via la CLI. Vous serez invité à saisir :

- Nom d’utilisateur (par défaut `admin`)
- Email (par défaut `admin@example.com`)
- Mot de passe (masqué, confirmé)

```bash
export FLASK_APP=manage.py
flask create-admin
```

## 4. Variables d’environnement

Placez ces variables dans un fichier `.env` (ou en environnement système) :

```ini
# Clé Flask
SECRET_KEY=changeme

# Base de données
DATABASE_URL=sqlite:///instance/app.db

# SMTP (Flask-Mail)
MAIL_SERVER=localhost
MAIL_PORT=8025
MAIL_USE_TLS=False
MAIL_USE_SSL=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@jofrance.com

# Environnement (dev | production)
FLASK_ENV=development
```

## 5. Lancement de l’application

```bash
# Mode développement (avec rechargement)
export FLASK_ENV=development
flask run --port=5000
```

Puis ouvrez `http://127.0.0.1:5002`.

## 6. Tests & Lint

- **Tests unitaires** :
  ```bash
  pytest --cov
  ```
  Affiche le rapport de couverture.

- **Lint & formatting** :
  ```bash
  black --check .
  flake8 .
  ```


