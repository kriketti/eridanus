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
                return redirect(url_for('crunches.index'))
    except (ValueError, Exception) as exc:
        error_message = str(exc)
        logger.exception(error_message)
    logger.debug(form)
    return render_template('activities/crunches/create.html', form=form, error_message=error_message)


@crunches.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    error_message = None
    form = CrunchesForm()
    
    if request.method == 'POST':
        try:
            if validate_form(form):
                service.update({
                    'id': id,
                    'activity_date': form.activity_date.data,
                    'activity_date': form.activity_date.data,
                    'activity_time': to_time(form.activity_time.data, '%H:%M'),
                    'duration': form.duration.data,
                    'calories': form.calories.data,
                    'count': form.count.data,
                    'notes': form.notes.data,
                    'usernickname': session['nickname']
                })
            flash('Activity "%s" saved successfully.', 'success')
            return redirect(url_for('crunches.index'))
        except (ValueError, Exception) as exc:
            error_message = str(exc)
            logger.exception(error_message)
        return render_template(
            'activities/crunches/edit.html',
            id=id,
            form=form)
    activity = service.read(id)
    if activity:
        form = CrunchesForm()
        form.activity_date.data = activity['activity_date']
        form.activity_time.data = activity['activity_time'].strftime('%H:%M')
        form.calories.data = activity['calories']
        form.count.data = activity['count']
        form.duration.data = activity['duration']
        form.notes.data = activity['notes']
        return render_template(
            'activities/crunches/edit.html',
            id=id,
            form=form)
    error = {'message': f"Jump rope activity was not found for id {id}"}
    return page_not_found(error)


@crunches.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html', error=e)



