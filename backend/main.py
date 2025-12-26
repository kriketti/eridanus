import logging
import os
import time

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from google.cloud import ndb

from config import Configuration
from eridanus.logging_config import configure_logging
from eridanus.admin.blueprint import admin
from eridanus.activities.crunches.blueprint import crunches
from eridanus.activities.jump_rope.blueprint import jump_rope_activities
from eridanus.activities.running.blueprint import running_activities
from eridanus.activities.pushups.blueprint import pushup_activities
from eridanus.dashboard.blueprint import dashboard
from eridanus.weighing.blueprint import weighings

from eridanus.api.v1 import api_blueprint

configure_logging()
logger = logging.getLogger(__name__)
app = Flask(__name__)
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, email):
        self.id = email
        self.email = email
        self.nickname = email.split('@', 1)[0]

@login_manager.user_loader
def load_user(email):
    return User(email)

app.config['DEBUG'] = True
# app.config['WTF_CSRF_SECRET_KEY'] = False
app.config['SECRET_KEY'] = Configuration.SECRET_KEY
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(crunches, url_prefix='/activities/crunches')
app.register_blueprint(jump_rope_activities, url_prefix='/activities/jump_rope')
app.register_blueprint(pushup_activities, url_prefix='/activities/pushups')
app.register_blueprint(running_activities, url_prefix="/activities/running")
app.register_blueprint(weighings, url_prefix='/weighings')
app.register_blueprint(dashboard, url_prefix='/dashboard')
app.register_blueprint(api_blueprint, url_prefix='/api/v1')

logger.info("Flask app initialized")

allowed_user_email = os.environ.get(
    'ALLOWED_USER_EMAIL',
    getattr(Configuration, 'ALLOWED_USER_EMAIL', None))
dev_user_email = os.environ.get(
    'DEV_USER_EMAIL',
    getattr(Configuration, 'DEV_USER_EMAIL', None))


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

def _get_iap_email():
    header_value = request.headers.get('X-Goog-Authenticated-User-Email', '')
    if header_value.startswith('accounts.google.com:'):
        return header_value.split(':', 1)[1]
    return None


def _resolve_user_email():
    email = _get_iap_email()
    if email:
        return email
    if app.config.get('DEBUG') and dev_user_email:
        return dev_user_email
    return None


def _is_allowed_email(email):
    if not allowed_user_email:
        return False
    return email.lower() == allowed_user_email.lower()


@app.before_request
def start_ndb_context():
    client = getattr(g, 'ndb_client', None)
    if client is None:
        client = ndb.Client()
        g.ndb_client = client
    ctx = client.context()
    ctx.__enter__()
    g.ndb_context = ctx
    g.request_start_time = time.monotonic()


@app.teardown_request
def end_ndb_context(exception):
    ctx = getattr(g, 'ndb_context', None)
    if ctx:
        ctx.__exit__(None, None, None)


@app.after_request
def log_request(response):
    start_time = getattr(g, "request_start_time", None)
    if start_time is not None:
        duration_ms = (time.monotonic() - start_time) * 1000.0
    else:
        duration_ms = None
    logger.info(
        "request completed",
        extra={
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
            "duration_ms": None if duration_ms is None else round(duration_ms, 2),
        },
    )
    return response


@app.before_request
def check_authentication():
    if current_user.is_authenticated:
        # Ensure legacy session variables are present
        if 'nickname' not in session:
            session['nickname'] = current_user.nickname
        return

    email = _resolve_user_email()
    if email and _is_allowed_email(email):
        user = User(email)
        login_user(user)
        session['user_email'] = email
        session['nickname'] = user.nickname
    else:
        abort(401)


@app.route('/')
@app.route('/home')
@csrf.exempt
def home():
    return redirect(url_for('dashboard.index'), 302)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404


@app.errorhandler(401)
def unauthorized(e):
    """Return not authorized."""
    return 'You''re not authorized to use this website', 401
