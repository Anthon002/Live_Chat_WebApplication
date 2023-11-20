from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class Registration(FlaskForm):
    Username = StringField("Username",validators=[DataRequired()])
    Password = PasswordField("Password", validators=[DataRequired()])
    ConfirmPassword = PasswordField("ConfirmPassword", validators=[DataRequired(), EqualTo("Password", message="Password does not match")])
    Submit = SubmitField("Register")