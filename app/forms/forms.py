from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app import db
from app.models.models import AppUser
import sqlalchemy

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    #todo shrink to single method
    def validate_username(self, username):
        user = db.session.scalar(sqlalchemy.select(AppUser).where(AppUser.username == username.data))
        if user is not None:
            raise ValidationError('Username is already in use!')

    def validate_email(self, email):
        user = db.session.scalar(sqlalchemy.select(AppUser).where(AppUser.email == email.data))
        if user is not None:
            raise ValidationError('Email is already in use!')

class ShortURLForm(FlaskForm):
    actual_url = TextAreaField('URL to point to', validators=[DataRequired(), Length(min=1, max=256)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=1, max=256)])
    submit = SubmitField('Submit')

