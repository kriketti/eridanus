import logging

from eridanus.utils.format import format_date, format_time
from eridanus.services import CrudService
from eridanus.repository import CrunchesRepository, JumpRopeRepository, PushUpsRepository, RunRepository
from eridanus.models import Activity, Run # Import models for ordering

logger = logging.getLogger(__name__)

class BaseActivityService(CrudService):

    def __init__(self, repository):
        self.repository = repository

    def fetch_all(self, username):
        items = []
        # Use NDB properties for ordering
        models = self.repository.fetch_by_username(username, order=[-Activity.activity_date, -Activity.activity_time])
        if models is not None:
            for model in models:
                # Use attribute access on the model object
                item = {'activity_time': format_time(model.activity_time),
                        'activity_date': format_date(model.activity_date),
                        'count': model.count,
                        'calories': model.calories,
                        'duration': model.duration,
                        'notes': model.notes,
                        'id': model.key.id() # Use id() method
                        }
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

class CrunchesService(BaseActivityService):

    def __init__(self):
        super(CrunchesService, self).__init__(CrunchesRepository())

class JumpRopeService(BaseActivityService):

    def __init__(self):
        super(JumpRopeService, self).__init__(JumpRopeRepository())

class PushupsService(BaseActivityService):

    def __init__(self):
        super(PushupsService, self).__init__(PushUpsRepository())


class RunningService(CrudService):

    def __init__(self, repository=None):
        self.repository = RunRepository()

    def fetch_all(self, username):
        items = self._fetch_all(username)
        records = self._compute_records(items)
        return {'items': items, 'records': records}

    def _fetch_all(self, username):
        items = []
        # Use NDB properties for ordering
        models = self.repository.fetch_by_username(username, order=[-Run.activity_date, -Run.activity_time])
        for model in models:
            duration = model.duration
            speed = 'N/A'
            
            # Check for attribute and its value, then calculate if needed
            if hasattr(model, 'speed') and model.speed:
                speed = model.speed
            elif model.distance and duration and duration > 0:
                speed = model.distance / (duration / 60.0)

            # Use attribute access on the model object
            item = {'duration': duration,
                    'distance': model.distance,
                    'speed': speed,
                    'activity_date': format_date(model.activity_date),
                    'activity_time': format_time(model.activity_time),
                    'calories': model.calories,
                    'id': model.key.id() # Use id() method
                    }
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
            
            # Ensure speed is a number before comparing
            current_speed = item.get('speed', 0.0)
            if isinstance(current_speed, (int, float)) and records['max_speed'] < current_speed:
                records['max_speed'] = current_speed
                
            if item.get('calories') and records['max_calories'] < item['calories']:
                records['max_calories'] = item['calories']
        return records

    def create(self, activity):
        self.repository.create(activity)

    def read(self, activity_id):
        logging.info(f'Read running entity having id {activity_id}')
        return self.repository.read(activity_id)

    def update(self, activity):
        self.repository.update(activity)

    def delete(self, activity_id):
        self.repository.delete(activity_id)