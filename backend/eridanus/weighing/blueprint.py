import logging

from flask import Blueprint, flash, render_template, \
    redirect, request, session, url_for
from flask_login import login_required

from eridanus.models import Weight
from eridanus.weighing.forms import WeightForm
from eridanus.weighing.services import WeighingService

logger = logging.getLogger(__name__)

weighings = Blueprint("weighings", __name__, template_folder='templates')
service = WeighingService()


@weighings.route("/")
@weighings.route("/list/")
def index():
    username = session['nickname']
    items = service.fetch_all(username)
    logger.debug(f'Received the following items: {items}')
    return render_template('weighings/index.html', vm=items)


@weighings.route("/create/", methods=['GET', 'POST'])
@login_required
def create():
    error_message = None
    form = WeightForm()
    try:
        if request.method == 'POST':
            logger.info(f'Received a POST request with data: {form}')
            if (form.validate()):
                username = session['nickname']
                service.create({
                    'usernickname': username,
                    'weight': float(0.0 if form.weight.data is None else form.weight.data),
                    'weighing_date': form.weighing_date.data
                })
                flash('Weighing record "%s" created successfully.', 'success')
                return redirect(url_for('weighings.index'))
    except (ValueError, Exception) as exc:
        error_message = str(exc)
        logger.exception(error_message)
    return render_template(
        'weighings/create.html',
        form=form,
        error_message=error_message)


@weighings.route("/edit/<id>/", methods=['GET', 'POST'])
def edit(id):
    error_message = None
    form = WeightForm()
    try:
        if request.method == 'POST':
            if (form.validate()):
                service.update({
                    'weight': float(form.weight.data),
                    'weighing_date': form.weighing_date.data,
                    'id': id
                })
                flash('Weighing record "%s" created successfully.', 'success')
                return redirect(url_for('weighings.index'))
        else:
            model = service.read(id)
            logger.debug(f'Got an weighting record: {model}')
            if not model:
                error = {}
                error['message'] = f"Weighing record was not found for id {id}"
                return page_not_found(error)
            form.weighing_date.data = model.weighing_date
            form.weight.data = model.weight
    except ValueError as exc:
        error_message = str(exc)
    return render_template(
        'weighings/edit.html',
        id=id,
        form=form,
        error_message=error_message)


@weighings.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html', error=e)
