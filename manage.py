import os
import click
from app.models import User
from app import app, db
from flask_migrate import Migrate

# Initialise Flask-Migrate
migrate = Migrate(app, db)

# CLI command to create admin user
@app.cli.command('create-admin')
@click.option('--username', prompt='Nom d’utilisateur', default='admin')
@click.option('--email', prompt='Email admin', default='admin@example.com')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,
              help='Mot de passe pour le compte admin')
def create_admin(username, email, password):
    """
    Crée un utilisateur admin si non existant.
    """
    if User.query.filter_by(username=username).first():
        click.echo(f"Le compte '{username}' existe déjà.")
        return
    admin = User( username=username, email=email )
    admin.is_admin = True
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Compte admin '{username}' créé avec succès.")

if __name__ == '__main__':
    app.run()