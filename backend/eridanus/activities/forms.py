from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, DecimalField, \
    StringField, TextAreaField
# from wtforms_components import TimeField
from wtforms.validators import DataRequired
from datetime import datetime


class ActivityForm(FlaskForm):
    activity_date = DateField(
        label='activity_date',
        default=datetime.now(),
        validators=[DataRequired()])
    activity_time = StringField(
        label='activity_time',
        default=datetime.now().time().strftime('%I:%M %p'),
        validators=[DataRequired()])
    duration = IntegerField()
    calories = IntegerField()
    notes = TextAreaField()


class CrunchesForm(ActivityForm):
    count = IntegerField()


class PushupForm(ActivityForm):
    count = IntegerField()


class RunningForm(ActivityForm):
    time = IntegerField(validators=[DataRequired()])
    distance = DecimalField(validators=[DataRequired()])
