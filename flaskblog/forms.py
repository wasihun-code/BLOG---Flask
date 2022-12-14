from flask_wtf import FlaskForm
from flaskblog.models import User
from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SubmitField,
    BooleanField,
    ValidationError,
)
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, EqualTo, Email
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign up")

    def validate_username(field, username):

        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError("username already taken. Choose a different one")

    def validate_email(field, email):

        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError("email already taken. Choose a different one")


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = EmailField("Email", validators=[DataRequired(), Email()])
    picture = FileField("Update Picture", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update")

    def validate_username(field, username):

        # if the username they entered is not theirs
        if username.data != current_user.username:
            
            # query the user
            user = User.query.filter_by(username=username.data).first()

            # if another user exists with the username
            if user:
                
                # raise valiadtion error
                raise ValidationError("username already taken. Choose a different one")

    def validate_email(field, email):

        # if the email they entered is not theirs
        if email.data != current_user.email:
            
            # query the user
            user = User.query.filter_by(email=email.data).first()

            # if anotehr user exists with that email
            if user:
                
                # raise validation error
                raise ValidationError("email already taken. Choose a different one")
