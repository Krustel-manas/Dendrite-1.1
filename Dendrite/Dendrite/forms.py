from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField
from Dendrite.models import User


class RegistrationForm(FlaskForm):
    role = SelectField(
        'Role:',
        choices=[('c', 'Company'), ('v', 'Vendor'), ('m', 'Manufacturer'), ('r', 'Retailer'), ('l', 'Logistics')]
    )
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    role = SelectField(
        'Role:',
        choices=[('v', 'Vendor'), ('m', 'Manufacturer'), ('r', 'Retailer'), ('l', 'Logistics'), ('c', 'Company')]
    )
    username = StringField('Username',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit Credentials')

class CreateTender(FlaskForm):
    cid = StringField('ContractID', validators=[DataRequired()])
    doi = StringField('DatePicker')
    vendor_address = StringField('VendorAddress', validators=[DataRequired()])
    file = FileField()
    submit = SubmitField('Create Contract')

class CreateAsset(FlaskForm):
    asset_name = StringField('AssetName', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Create Asset')