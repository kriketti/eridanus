import logging

from datetime import datetime
from flask import Blueprint, flash, redirect, \
    render_template, request, session, url_for
from flask_login import login_required
from eridanus.activities.forms import JumpRopeForm
from eridanus.activities.services import JumpRopeService
from eridanus.utils.form import validate_form
from eridanus.utils.format import to_time


logger = logging.getLogger(__name__)


jump_rope_activities = Blueprint(
    'jump_rope_activities',
    __name__,
    template_folder='templates')
service = JumpRopeService()


@jump_rope_activities.route("/")
@jump_rope_activities.route("/list/")
@login_required
def index():
    username = session['nickname']
    items = service.fetch_all(username)
    return render_template(
        'activities/jump_rope/index.html', viewmodel={'items': items})



@jump_rope_activities.route("/create/", methods=['GET', 'POST'])
@login_required
def create():
    error_message = None
    form = JumpRopeForm()
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
                flash('Jump rope activity "%s" created successfully.', 'success')
                return redirect(url_for('jump_rope_activities.index'), 302)
    except (ValueError, Exception) as exc:
        error_message = str(exc)
        logger.exception(error_message)
    logger.debug(form)
    return render_template('activities/jump_rope/create.html', form=form, error_message=error_message)


@jump_rope_activities.route('/<id>/', methods=['GET', 'POST'])
@login_required
def view(id):
    ''' REVIEW: TEST: TODO: '''
    model = service.read(id)
    if model:
        return render_template('activities/jump_rope/view.html', model=model)
    return redirect(url_for('app.page_not_found', 302))


@jump_rope_activities.route("/<activity_id>/edit", methods=['GET', 'POST'])
@login_required
def edit(activity_id):
    form = JumpRopeForm()
    if request.method == 'POST':
        if validate_form(form):
            service.update({
                'id': activity_id,
                'activity_date': form.activity_date.data,
                'activity_time': to_time(form.activity_time.data,'%H:%M'),
                'calories': form.calories.data,
                'count': form.count.data,
                'duration': form.duration.data,
                'notes': form.notes.data,
                'user_nickname': session['nickname']
            })
            flash('Jump rope activity "%s" saved successfully.', 'success')
            return redirect(url_for('jump_rope_activities.index'), 302)
    activity = service.read(activity_id)
    if activity:
        form = JumpRopeForm()
        form.activity_date.data = activity['activity_date']
        return render_template(
            'activities/jump_rope/edit.html',
            form=form)
    error = {'message': f"Jump rope activity was not found for id {activity_id}"}
    return page_not_found(error)


@jump_rope_activities.route("/<activity_id>/delete/", methods=['POST'])
def delete(activity_id):
    service.delete(activity_id)
    flash('Jump rope activity "%s" saved successfully.', 'success')
    return redirect(url_for('jump_rope_activities.index'), 302)


@jump_rope_activities.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html', error=e)
