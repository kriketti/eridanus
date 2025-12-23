from flask import Blueprint, render_template, session
# from flask.ext.login import login_required
from .services import DashboardService


dashboard = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard.route('/', methods=['GET'])
def index():
    username = session['nickname']
    if username:
        stats = DashboardService().home_stats(username)
        return render_template('dashboard/index.html', stats=stats)
    else:
        pass
