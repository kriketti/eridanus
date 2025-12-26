
from flask import flash

def validate_form(form):
    if not form.validate():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
        return False
    return True