from flask import Blueprint, make_response, render_template, session, abort, jsonify
from flask_login import login_required, current_user
from io import BytesIO
from zipfile import ZipFile
from eridanus.admin.services import ExportDataService, ImportDataServices
from eridanus.admin.migration_add_speed import migrate_runs
from google.cloud import ndb
from config import Configuration # Assuming Configuration is accessible here, or import from main if not.

admin = Blueprint('admin', __name__, template_folder='templates')


def _zip(file, data_streams):
    zip = ZipFile(file, 'a')
    for key in data_streams:
        filename = key + '.csv'
        zip.writestr(filename, data_streams[key])
    for f in zip.filelist:
        f.create_system = 0
    zip.close()
    file.seek(0)
    return file


def _zip_in_memory(data_streams):
    file = BytesIO()
    return _zip(file, data_streams)


@admin.route('/', methods=['GET'])
@login_required
def index():
        return render_template('admin/home.html')


@admin.route('/export/<format>/', methods=['GET'])
@login_required
def export(format):
    service = ExportDataService()
    username = session['nickname']
    data = {}
    data['run'] = service.get_run_data(username, format)
    data['weight'] = service.get_weight_data(username, format)
    zip_stream = _zip_in_memory(data)
    response = make_response(zip_stream.getvalue())
    response.headers["Content-Disposition"] = 'attachment;' \
        + 'filename=eridanus_data.zip'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'application/zip'
    # in_memory.seek(0)    
    # response.write(in_memory.read()) #?
    return response


@admin.route('/import/<folder>', methods=['GET'])
@login_required
def import_index(folder):
    service = ImportDataServices()
    username = session['nickname']
    data = service.import_from_csv(folder, username)
    response = make_response()
    response.headers['Content-Type'] = 'text/plain'
    response.set_data(str(data))
    return response

@admin.route('/run_speed_migration', methods=['POST']) # Changed to POST to prevent accidental GET
@login_required
def run_speed_migration():
    # Ensure only the allowed admin user can trigger this
    if current_user.email != Configuration.ALLOWED_USER_EMAIL:
        abort(403) # Forbidden
    
    # The ndb.Client context should be managed by the Flask app's before/teardown request hooks
    # So we just need to call the migration function.
    try:
        migrate_runs()
        return jsonify({"status": "success", "message": "Migrarea speed-ului a fost rulată cu succes!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Eroare la rularea migrării: {str(e)}"}), 500
