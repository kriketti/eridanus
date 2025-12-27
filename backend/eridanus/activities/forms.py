import logging

from flask import flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, DecimalField, \
    StringField, TextAreaField
# from wtforms_components import TimeField
from wtforms.validators import DataRequired
from datetime import datetime

logger = logging.getLogger(__name__)

class ActivityForm(FlaskForm):
    activity_date = DateField(
        label='activity_date',
        default=datetime.now(),
        validators=[DataRequired()])
    activity_time = StringField(
        label='activity_time',
        default=datetime.now().time().strftime('%H:%M'),
        validators=[DataRequired()])
    calories = IntegerField()
    notes = TextAreaField()

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            for field_name in list(self.errors.keys()):
                field = getattr(self, field_name, None)
                if field:
                    is_required = getattr(field.flags, 'required', False)
                    is_empty = not field.raw_data or not str(field.raw_data[0]).strip()

                    logger.debug("Field raw data: %s, is_required: %s, is_empty: %s", field.raw_data, is_required, is_empty)
                    
                    if not is_required and is_empty:
                        # Remove the error from form
                        del self.errors[field_name]
                        # Remove the errors from field
                        field.errors = []
                        field.data = None

            if not self.errors:
                return True

            for field, errors in self.errors.items():
                for error in errors:
                    logger.error(f"Form validation error: {getattr(self, field).label.text}: {error}")
                    flash(f"{getattr(self, field).label.text}: {error}", 'danger')
            return False
        return True


class CountableExerciseForm(ActivityForm):
    duration = IntegerField()
    count = IntegerField()

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        if not (self.duration.data or self.count.data):
            error_message = "You must enter either duration of the activity or the number of exercises or both"
            flash(error_message, 'danger')
            return False
        return True

class CrunchesForm(CountableExerciseForm):
    pass

class JumpRopeForm(CountableExerciseForm):
    pass

class PushupForm(CountableExerciseForm):
    pass

class RunningForm(ActivityForm):
    duration = IntegerField(validators=[DataRequired()])
    distance = DecimalField(validators=[DataRequired()])
