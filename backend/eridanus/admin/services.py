from ..utils import to_date, to_time, to_datetime
from google.cloud import storage
from io import StringIO

import csv
import os
import eridanus.repository as repository

IMPORT_DATE_FORMAT = '%Y-%m-%d'
IMPORT_TIME_FORMAT = '%H:%M:%S'
IMPORT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class ExportDataService(object):

    def get_run_data(self, username, format):
        repo = repository.RunRepository()
        items = repo.fetch_all(username)
        stream = StringIO()
        fieldnames = ['usernickname', 'activity_date', 'activity_time',
                      'time', 'distance', 'speed', 'calories', 
                      'notes', 'creation_datetime']
        csvwriter = csv.DictWriter(
                        stream,
                        fieldnames=fieldnames,
                        dialect='excel')
        csvwriter.writeheader()
        for item in items:
            csvwriter.writerow({
                'usernickname': item.usernickname, 
                'activity_date': item.activity_date,
                'activity_time': item.activity_item,
                'duration': item.duration,
                'distance': item.distance,
                'speed': item.speed,
                'calories': item.calories,
                'notes': item.notes,
                'creation_datetime': item.creation_datetime
                })
        return stream.getvalue()

    def get_weight_data(self, username, format):
        repo = repository.WeightRepository()
        items = repo.fetch_all(username)
        stream = StringIO()
        csvwriter = csv.writer(stream, dialect='excel')
        fieldnames = ['usernickname', 'weight', 'creation_datetime']
        csvwriter = csv.DictWriter(
            stream,
            fieldnames=fieldnames,
            dialect='excel')
        csvwriter.writeheader()
        for item in items:
            csvwriter.writerow({
                'usernickname': item.usernickname,
                'weight': item.weight,
                'creation_datetime': item.creation_datetime
                })
        return stream.getvalue()


class ImportDataServices(object):

    def import_from_csv(self, folder, username):
        audit = {}
        bucket = self._get_default_bucket()
        audit['default_bucket'] = bucket.name if bucket else None
        if bucket:
            import_folder = 'import/' + folder
            # self._import_run_csv(bucket, import_folder)
            self._import_weight_csv(bucket, import_folder)
        return audit

    def _get_default_bucket(self):
        bucket_name = os.environ.get('BUCKET_NAME')
        if not bucket_name:
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
            if project_id:
                bucket_name = project_id + '.appspot.com'
        if not bucket_name:
            return None
        client = storage.Client()
        return client.bucket(bucket_name)

    def _read_file(self, bucket, filename):
        blob = bucket.blob(filename)
        return blob.download_as_bytes()

    def _import_run_csv(self, bucket, import_folder):
        audit = {}
        filename = import_folder + '/run.csv'
        content = self._read_file(bucket, filename)
        stream = StringIO(content.decode('utf-8'))
        csvReader = csv.DictReader(stream, dialect='excel')
        for row in csvReader:
            repo = repository.RunRepository()
            duration = int(row['duration'])
            distance = float(row['distance'])
            speed = None
            if row['speed']:
                speed = float(row['speed'])
            else:
                speed = distance / (duration / 60.0)
            repo.create({
                'user_nickname': row['usernickname'],
                'activity_date': to_date(
                    row['activity_date'], IMPORT_DATE_FORMAT),
                'activity_time': to_time(
                    row['activity_time'], IMPORT_TIME_FORMAT),
                'duration': duration,
                'distance': distance,
                'speed': speed,
                'calories': int(row['calories']),
                'notes': row['notes'],
                'creation_datetime': to_datetime(
                    row['creation_datetime'], IMPORT_DATETIME_FORMAT)
            })
        audit['filename'] = filename
        return audit

    def _import_weight_csv(self, bucket, import_folder):
        filename = import_folder + '/weight.csv'
        content = self._read_file(bucket, filename)
        stream = StringIO(content.decode('utf-8'))
        csvReader = csv.DictReader(stream, dialect='excel')
        for row in csvReader:
            repo = repository.WeightRepository()
            repo.create({
                'user_nickname': row['usernickname'],
                'weight': float(row['weight']),
                'weighing_date': to_date(
                    row['creation_datetime'], IMPORT_DATETIME_FORMAT),
                'creation_datetime': to_datetime(
                    row['creation_datetime'], IMPORT_DATETIME_FORMAT)
            })
