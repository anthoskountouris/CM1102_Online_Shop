from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, InputRequired, NumberRange
from shop.models import User

"""
def invalid_credentials(form,field):
  email = form.email.data
  password = field.data

  user = User.query.filter_by(email=email).first()
  if user is None:
    raise ValidationError('Email or password is incorrect.')
  elif password != user.password:
    raise ValidationError('Email or password is incorrect.')

"""


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('A username is required!'), Length(
        min=5, max=15, message='Must be between 5 to 15 characters!')])
    email = StringField('Email', validators=[
                        InputRequired('An email is required!'), Email()])
    password = PasswordField('Password', validators=[InputRequired('A password is required!'), Regexp(
        '^.{6,8}$', message='Your password should bebetween 6 and 8 characters long.')])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     InputRequired('Please confirm password'), EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(
                'Username already exist. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(
                'Email address is already associated with an account.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                        InputRequired('An email is required!'), Email()])
    password = PasswordField('Password', validators=[
                             InputRequired('A password is required!')])


class checkoutForm(FlaskForm):
    ship_name = StringField('Shipping name', validators=[
        InputRequired('Your name is required')])
    ship_street = StringField(
        'Address 1st line', validators=[InputRequired()])
    ship_town = StringField('Town', validators=[InputRequired()])
    ship_postcode = StringField('Postcode', validators=[InputRequired(), Length(
        min=6, max=8, message="Post Codes are 6-8 characters long")])
    card_number = IntegerField('Card Number', validators=[InputRequired(), NumberRange(
        min=1, max=9999999999999999, message="Card Number are 16 characters long")])
    card_ccv = IntegerField('CCV', validators=[InputRequired(), NumberRange(
        min=1, max=999, message="CCV are 3 characters long")])


class reviewForm(FlaskForm):
    star_rating = SelectField('Star rating',
                              choices=[(1, "1 star"), (2, "2 stars"),
                                       (3, "3 stars"), (4, "4 stars"), (5, "5 stars")],
                              coerce=int,
                              validators=[InputRequired("Please award a star-rating")])
    content = TextAreaField('Content', validators=[
                            InputRequired("Please enter a review of the item")])
