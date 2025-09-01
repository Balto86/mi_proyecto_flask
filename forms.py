from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProductoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    cantidad = IntegerField("Cantidad", validators=[DataRequired(), NumberRange(min=0)])
    precio = FloatField("Precio", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Guardar")
