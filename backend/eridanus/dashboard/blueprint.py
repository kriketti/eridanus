from flask import Blueprint, render_template, session
from flask_login import login_required
from .services import DashboardService

import logging

logger = logging.getLogger(__name__)


dashboard = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard.route('/', methods=['GET'])
@login_required
def index():
    error_message = None
    stats = None
    try:
        username = session.get('nickname')
        service = DashboardService()
        stats = service.home_stats(username)
    except ValueError as exc:
        logger.exception(exc)
        error_message = str(exc)
    except Exception:
        logger.exception("Eroare neasteptata la incarcarea dashboard-ului")
        error_message = "A aparut o eroare interna. Te rugam sa incerci din nou mai tarziu."
    return render_template('dashboard/index.html', stats=stats, error_message=error_message)
