from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DecimalField, IntegerField, DateField, SubmitField, HiddenField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional, Email, Length
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    otp_token = StringField('6-digit Code (if 2FA enabled)', validators=[Optional(), Length(min=6, max=6)])
    submit = SubmitField('Log In')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    barcode = StringField('Barcode', validators=[Optional()])
    batch_number = StringField('Batch Number', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    supplier_id = SelectField('Supplier', coerce=int, validators=[Optional()])
    purchase_price = DecimalField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    selling_price = DecimalField('Selling Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    expiry_date = DateField('Expiry Date (YYYY-MM-DD)', validators=[DataRequired()])
    submit = SubmitField('Save Product')

class SupplierForm(FlaskForm):
    name = StringField('Supplier Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    address = StringField('Address', validators=[Optional()])
    submit = SubmitField('Save Supplier')

class PurchaseForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    supplier_id = SelectField('Supplier', coerce=int, validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    buying_price = DecimalField('Buying Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Stock')

class StockTransferForm(FlaskForm):
    from_branch_id = SelectField('From Branch', coerce=int, validators=[DataRequired()])
    to_branch_id = SelectField('To Branch', coerce=int, validators=[DataRequired()])
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Transfer')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    branch_id = SelectField('Branch', coerce=int, validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save User')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Category')