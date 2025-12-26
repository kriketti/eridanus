from flask import Blueprint, make_response, render_template, session
from flask_login import login_required
from io import BytesIO
from zipfile import ZipFile
from .services import ExportDataService, ImportDataServices


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
