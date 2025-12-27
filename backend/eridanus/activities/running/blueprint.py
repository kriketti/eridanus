import logging

from flask import Blueprint, flash, render_template, \
    redirect, session, request, url_for
from flask_login import login_required
from eridanus.activities.forms import RunningForm
from eridanus.activities.services import RunningService
from eridanus.utils.format import to_time


logger = logging.getLogger(__name__)

service = RunningService()

running_activities = Blueprint(
    'running_activities',
    __name__,
    template_folder='templates')


@running_activities.route("/")
@running_activities.route("/list/")
@login_required
def index():
    ''' create the viewmodel and return the view '''
    username = session['nickname']
    items = service.fetch_all(username)
    return render_template('activities/running/index.html', vm=items)


@running_activities.route("/create/", methods=["GET", "POST"])
@login_required
def create():
    error_message = None
    form = RunningForm()
    try:
        if request.method == "POST":
            if form.validate():
                distance = float(form.distance.data)
                duration = form.duration.data
                speed = distance / (float(duration)/60.0)

                service.create({
                        'activity_date': form.activity_date.data,
                        'activity_time': to_time(form.activity_time.data),
                        'distance': distance,
                        'duration': duration,
                        'calories': form.calories.data,
                        'notes': form.notes.data,
                        'speed': speed,
                        'usernickname': session['nickname']
                    })
                flash('Running activity created successfully.', 'success')
                return redirect(url_for('running_activities.index'))
    except (ValueError, Exception) as exc:
        error_message = str(exc)
        logger.exception(exc)
    return render_template(
        'activities/running/create.html',
        form=form,
        error_message=error_message)


@running_activities.route("/edit/<id>/", methods=["GET", "POST"])
def edit(id):
    error_message = None
    form = RunningForm()
    try:
        if request.method == "POST":
            if form.validate():
                distance = float(form.distance.data)
                duration = form.duration.data
                speed = distance / (float(duration)/60.0)

                service.update({
                        'id': id,
                        'activity_date': form.activity_date.data,
                        'activity_time': to_time(form.activity_time.data),
                        'distance': distance,
                        'duration': duration,
                        'calories': form.calories.data,
                        'notes': form.notes.data,
                        'speed': speed
                    })
                flash('Running activity updated successfully.', 'success')
                return redirect(url_for('running_activities.index'))
        else:
            activity = service.read(id)
            if not activity:
                error = {'message': f"Running activity was not found for id {id}"}
                return page_not_found(error)
            form.activity_date.data = activity.activity_date
            form.activity_time.data = activity.activity_time.strftime('%H:%M')
            form.duration.data = activity.duration
            form.calories.data = activity.calories
            form.distance.data = activity.distance
            form.notes.data = activity.notes
    except (ValueError, Exception) as exc:
        error_message = str(exc)
        logger.exception(exc)
    return render_template(
        'activities/running/edit.html',
        id=id,
        form=form,
        error_message=error_message)



@running_activities.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html')
