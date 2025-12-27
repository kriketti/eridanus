import logging

from datetime import datetime
from flask import Blueprint, flash, redirect, \
    render_template, request, session, url_for
from flask_login import login_required
from eridanus.activities.forms import PushupForm
from eridanus.activities.services import PushupsService
from eridanus.utils.format import to_time
from eridanus.utils.form import validate_form

logger = logging.getLogger(__name__)

pushup_activities = Blueprint(
    'pushup_activities',
    __name__,
    template_folder='templates')
service = PushupsService()


@pushup_activities.route("/")
@pushup_activities.route("/list/")
@login_required
def index():
    username = session['nickname']
    items = service.fetch_all(username)
    return render_template(
        'activities/pushups/index.html', viewmodel={'items': items})


@pushup_activities.route("/create/", methods=['GET', 'POST'])
@login_required
def create():
    error_message = None
    form = PushupForm()
    try:
        if request.method == 'POST':
            if validate_form(form):
                service.create({
                    'activity_date': form.activity_date.data,
                    'activity_time': to_time(form.activity_time.data,'%H:%M'),
                    'calories': form.calories.data,
                    'count': form.count.data,
                    'duration': form.duration.data,
                    'notes': form.notes.data,
                    'usernickname': session['nickname']
                    })
                flash('Push-ups activity "%s" created successfully.', 'success')
                return redirect(url_for('pushup_activities.index'), 302)
    except (ValueError, Exception) as exc:
        error_message = str(exc)
        logger.exception(error_message)
    logger.debug(form)
    return render_template('activities/pushups/create.html', form=form, error_message=error_message)


@pushup_activities.route('/<id>/', methods=['GET', 'POST'])
def view(id):
    activity = service.read(id)
    if activity:
        return render_template('activities/pushups/view.html', activity=activity)
    else:
        return redirect(url_for('app.page_not_found'))


@pushup_activities.route("/edit/<id>/", methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        form = PushupForm()
        if validate_form(form):
            service.update({
                'id': id,
                'activity_date': form.activity_date.data,
                'activity_time': to_time(
                    form.activity_time.data,
                    '%H:%M'
                    ),
                'calories': form.calories.data,
                'count': form.count.data,
                'duration': form.duration.data,
                'notes': form.notes.data,
                'usernickname': session['nickname']
            })
            flash('Push-ups activity "%s" saved successfully.', 'success')
            return redirect(url_for('pushup_activities.index'))
    activity = service.read(id)
    if activity:
        form = PushupForm()
        form.activity_date.data = activity['activity_date']
        form.activity_time.data = activity['activity_time'].strftime('%H:%M')
        form.calories.data = activity['calories']
        form.count.data = activity['count']
        form.duration.data = activity['duration']
        form.notes.data = activity['notes'] 
        return render_template(
            'activities/pushups/edit.html',
            id=id,
            form=form)
    error = {'message': f"Push-ups activity was not found for id {id}"}
    return page_not_found(error)


@pushup_activities.route("/<activity_id>/delete/", methods=['POST'])
def delete(activity_id):
    service.delete(activity_id)
    flash('Push-ups activity "%s" saved successfully.', 'success')
    return redirect(url_for('pushup_activities.index'))


@pushup_activities.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html', error=e)
