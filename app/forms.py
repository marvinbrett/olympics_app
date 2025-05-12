# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    username  = StringField('Nom d’utilisateur', validators=[DataRequired()])
    email     = StringField('Email', validators=[DataRequired(), Email()])
    password  = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Confirmez le mot de passe', validators=[
                    DataRequired(), EqualTo('password', message="Les mots de passe doivent correspondre.")])
    submit    = SubmitField("S'inscrire")

class LoginForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit   = SubmitField("Se connecter")

class OfferForm(FlaskForm):
    name     = StringField('Nom de l’offre', validators=[DataRequired()])
    price    = IntegerField('Prix (€)', validators=[DataRequired(), NumberRange(min=0)])
    capacity = IntegerField('Capacité', validators=[DataRequired(), NumberRange(min=1)])
    submit   = SubmitField("Ajouter l’offre")