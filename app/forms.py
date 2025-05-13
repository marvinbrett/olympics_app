# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField(
        'Nom d’utilisateur',
        validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[DataRequired(), Length(min=6)]
    )
    password2 = PasswordField(
        'Confirmez le mot de passe',
        validators=[
            DataRequired(),
            EqualTo('password', message='Les mots de passe doivent correspondre')
        ]
    )
    submit = SubmitField("S'inscrire")

class LoginForm(FlaskForm):
    username = StringField(
        'Nom d’utilisateur',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[DataRequired()]
    )
    submit = SubmitField("Connexion")

class OfferForm(FlaskForm):
    name = StringField(
        "Nom de l'offre",
        validators=[DataRequired()]
    )
    price = FloatField(
        "Prix",
        validators=[DataRequired()]
    )
    capacity = IntegerField(
        "Capacité",
        validators=[DataRequired()]
    )
    submit = SubmitField("Ajouter")


class EmptyForm(FlaskForm):
    """Formulaire vide juste pour le CSRF."""
    submit = SubmitField()  # on n'en a pas vraiment besoin mais WTForms exige au moins un field