import logging

from flask import Blueprint, flash, \
    redirect, render_template, request, session, url_for
from flask_login import login_required
from ..forms import CrunchesForm
from ..services import CrunchesService
from eridanus.utils.format import date_to_datetime, to_time, time_to_datetime
from eridanus.utils.form import validate_form

logger = logging.getLogger(__name__)

crunches = Blueprint('crunches', __name__, template_folder='templates')
service = CrunchesService()


@crunches.route('/', methods=['GET'])
@crunches.route('/list/', methods=['GET'])
@login_required
def index():
    username = session['nickname']
    items = service.fetch_all(username)
    logger.debug(f'Received the following items: {items}')

    return render_template(
        'activities/crunches/index.html',
        viewmodel={'items': items})


@crunches.route('/create/', methods=['GET', 'POST'])
def create():
    error_message = None
    form = CrunchesForm()
    try:
        if request.method == 'POST':
            if validate_form(form):
                service.create({
                    'activity_date': form.activity_date.data,
                    'activity_time': to_time(form.activity_time.data, '%H:%M'),
                    'duration': form.duration.data,
                    'calories': form.calories.data,
                    'count': form.count.data,
                    'notes': form.notes.data,
                    'usernickname': session['nickname']
                })
                flash('Activity "%s" created successfully.', 'success')
                return redirect(url_for('crunches.index'), 302)
    except (ValueError, Exception) as exc:
        error_message = str(exc)
        logger.exception(error_message)
    logger.debug(form)
    return render_template('activities/crunches/create.html', form=form, error_message=error_message)



