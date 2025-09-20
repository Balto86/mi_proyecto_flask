from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo, Length

class ProductoForm(FlaskForm):
    """Formulario para gestionar productos."""
    nombre = StringField("Nombre", validators=[DataRequired()])
    cantidad = IntegerField("Cantidad", validators=[DataRequired(), NumberRange(min=0)])
    precio = FloatField("Precio", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Guardar Producto")

class RegistrationForm(FlaskForm):
    """Formulario de registro de usuario."""
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    """Formulario de inicio de sesión de usuario."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')
