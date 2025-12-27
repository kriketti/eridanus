import logging

from flask import Blueprint, flash, \
    redirect, render_template, request, session, url_for
from flask_login import login_required
from ..forms import CrunchesForm
from ..services import CrunchesService
from eridanus.utils.format import to_time

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
            if form.validate():
                # Start with required fields
                crunch_data = {
                    'activity_date': form.activity_date.data,
                    'activity_time': to_time(form.activity_time.data),
                    'usernickname': session['nickname']
                }
                
                # Conditionally add optional fields only if they have a value
                if form.duration.data is not None:
                    crunch_data['duration'] = form.duration.data
                if form.calories.data is not None:
                    crunch_data['calories'] = form.calories.data
                if form.count.data is not None:
                    crunch_data['count'] = form.count.data
                if form.notes.data:
                    crunch_data['notes'] = form.notes.data

                service.create(crunch_data)
                flash('Activity created successfully.', 'success')
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
            if form.validate():
                service.update({
                    'id': id,
                    'activity_date': form.activity_date.data,
                    'activity_time': to_time(form.activity_time.data),
                    'duration': form.duration.data,
                    'calories': form.calories.data,
                    'count': form.count.data,
                    'notes': form.notes.data
                })
            flash(f'Activity saved successfully.', 'success')
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
        form.activity_date.data = activity.activity_date
        form.activity_time.data = activity.activity_time.strftime('%H:%M')
        form.calories.data = activity.calories
        form.count.data = activity.count
        form.duration.data = activity.duration
        form.notes.data = activity.notes
        return render_template(
            'activities/crunches/edit.html',
            id=id,
            form=form)
    error = {'message': f"Jump rope activity was not found for id {id}"}
    return page_not_found(error)


@crunches.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html', error=e)
