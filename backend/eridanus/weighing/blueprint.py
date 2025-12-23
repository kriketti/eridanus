from flask import Blueprint, flash, render_template, \
    redirect, request, session, url_for
from .forms import WeightForm
from .services import WeighingService


weighings = Blueprint("weighings", __name__, template_folder='templates')
service = WeighingService()


@weighings.route("/")
@weighings.route("/list/")
def index():
    username = session['nickname']
    items = service.fetch_all(username)
    return render_template('weighings/index.html', vm=items)


@weighings.route("/create/", methods=['GET', 'POST'])
def create():
    form = WeightForm()
    if form.validate_on_submit():
        service.create({
            'user_nickname': session['nickname'],
            'weight': float(form.weight.data),
            'weighing_date': form.weighing_date.data
        })
        flash('Weighing record created successfully.', 'success')
        return redirect(url_for('weighings.index'))
    return render_template('weighings/create.html', form=form)
