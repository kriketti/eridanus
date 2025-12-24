from ..utils import format_date, format_time
from ..services import CrudService


class CrunchesService(CrudService):

    def __init__(self):
        from eridanus.repository import CrunchesRepository
        self.repository = CrunchesRepository()

    def fetch_all(self, username):
        items = []
        models = self.repository.fetch_all(username)
        if models is not None:
            for model in models:
                item = {'activity_time': format_time(model.activity_time),
                        'activity_date': format_date(model.activity_date),
                        'count': model.count,
                        'calories': model.calories,
                        'duration': model.duration,
                        'notes': model.notes}
                items.append(item)
        return items

    def create(self, activity):
        return self.repository.create(activity)

    def read(self, activity_id):
        return self.repository.read(activity_id)

    def update(self, activity):
        return self.repository.update(activity)

    def delete(self, activity_id):
        return self.repository.delete(activity_id)


class PushupsService(CrudService):
    ''' Push-ups controller '''

    def __init__(self):
        from eridanus.repository import PushUpsRepository
        self.repository = PushUpsRepository()

    def fetch_all(self, username):
        ''' creates and returns the view and viewmodel '''
        items = []
        models = self.repository.fetch_all(username)
        if models is not None:
            for model in models:
                item = {'activity_time': format_time(model.activity_time),
                        'activity_date': format_date(model.activity_date),
                        'count': model.count,
                        'calories': model.calories,
                        'duration': model.duration,
                        'notes': model.notes}
                items.append(item)
        return items

    def create(self, activity):
        self.repository.create(activity)

    def read(self, activity_id):
        return NotImplemented

    def update(self, activity):
        return NotImplemented

    def delete(self, activity_id):
        return NotImplemented


class RunningService(CrudService):

    def __init__(self):
        from eridanus.repository import RunRepository
        self.repository = RunRepository()

    def fetch_all(self, username):
        items = self._fetch(username)
        records = self._compute_records(items)
        return {'items': items, 'records': records}

    def _fetch(self, username):
        items = []
        models = self.repository.fetch_all(username)
        for model in models:
            duration = model.duration
            speed = 'N/A'
            if model.speed:
                speed = model.speed
            else:
                speed = model.distance / (duration / 60.0)

            item = {'duration': duration,
                    'distance': model.distance,
                    'speed': speed,
                    'activity_date': format_date(model.activity_date),
                    'activity_time': format_time(model.activity_time),
                    'calories': model.calories}
            items.append(item)
        return items

    def _compute_records(self, items):
        records = {'max_distance': 0,
                   'max_time': 0,
                   'max_speed': 0.0,
                   'max_calories': 0}
        for item in items:
            if records['max_distance'] < item['distance']:
                records['max_distance'] = item['distance']
            if records['max_time'] < item['duration']:
                records['max_time'] = item['duration']
            if records['max_speed'] < item['speed']:
                records['max_speed'] = item['speed']
            if item['calories'] is not None and \
                    records['max_calories'] < item['calories']:
                records['max_calories'] = item['calories']
        return records

    def create(self, activity):
        self.repository.create(activity)

    def read(self, activity_id):
        return NotImplemented

    def update(self, activity):
        return NotImplemented

    def delete(self, activity_id):
        return NotImplemented