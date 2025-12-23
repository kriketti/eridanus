from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import DecimalField, DateField
from wtforms.validators import DataRequired


class WeightForm(FlaskForm):
    weighing_date = DateField(
        label='weighing_date',
        default=datetime.now(),
        validators=[DataRequired()])
    weight = DecimalField(label='weight', validators=[DataRequired()])
