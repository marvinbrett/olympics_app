import os

from app import app, db
from flask_migrate import Migrate

# Initialise Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()