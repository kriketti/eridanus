import logging
from datetime import datetime
from google.cloud import ndb

from eridanus.models import Crunch, Run, Weight, PushUp, JumpingRope

logger = logging.getLogger(__name__)


class Repository(object):
    """
    Base repository class. It's empty because NDB context management
    is handled globally in main.py, not per-repository instance.
    """
    pass


class CrudRepository(Repository):
    """
    A generic repository providing CRUD (Create, Read, Update, Delete)
    operations for any NDB model.
    """

    def __init__(self, model_class):
        """
        Initializes the repository for a specific model class.
        :param model_class: The NDB model class (e.g., Weight, Run).
        """
        super(CrudRepository, self).__init__()
        self.model_class = model_class

    def create(self, record):
        """
        Creates and saves a new entity from a dictionary.
        """
        logger.debug(f'Creating record of kind {self.model_class.__name__}: {record}')
        
        # Add the creation datetime automatically
        if 'creation_datetime' not in record:
            record['creation_datetime'] = datetime.now()

        # Instantiate the NDB model object and save it
        entity = self.model_class(**record)
        entity.put()
        return entity

    def delete(self, identifier):
        """
        Deletes an entity by its numeric ID.
        """
        try:
            key = ndb.Key(self.model_class, int(identifier))
            return key.delete()
        except (ValueError, TypeError) as e:
            logger.error(f"Could not delete {self.model_class.__name__} with identifier {identifier}: Invalid ID. {e}")
            return None

    def fetch_all(self):
        """
        Fetches all entities of this kind.
        Orders by 'activity_date' descending if the property exists.
        """
        query = self.model_class.query()
        if hasattr(self.model_class, 'activity_date'):
            query = query.order(-self.model_class.activity_date)
        return query.fetch()

    def fetch_by_username(self, username, order=None):
        """
        Fetches entities for a specific user, with optional ordering.
        :param order: A list of NDB properties to order by, e.g., [-Weight.weighing_date]
        """
        query = self.model_class.query(self.model_class.usernickname == username)
        if order:
            for o in order:
                query = query.order(o)
        return query.fetch()

    def read(self, identifier):
        """
        Reads a single entity by its numeric ID.
        """
        try:
            return self.model_class.get_by_id(int(identifier))
        except (ValueError, TypeError):
            logger.warning(f"Could not read {self.model_class.__name__}: Invalid identifier '{identifier}'.")
            return None

    def update(self, record):
        """
        Updates an existing entity from a dictionary.
        The dictionary must contain an 'id'.
        """
        identifier = record.pop('id', None)
        if not identifier:
            raise ValueError(f"Record for {self.model_class.__name__} must contain an 'id' for update.")

        entity = self.read(identifier)
        if entity:
            # Use populate to update the entity's properties from the dictionary
            entity.populate(**record)
            entity.put()
        else:
            logger.warning(f"Could not update {self.model_class.__name__}: No entity found for id {identifier}.")
        return entity


# Specific repositories now pass the actual model class
class CrunchesRepository(CrudRepository):
    def __init__(self):
        super(CrunchesRepository, self).__init__(Crunch)


class JumpRopeRepository(CrudRepository):
    def __init__(self):
        super(JumpRopeRepository, self).__init__(JumpingRope)


class PushUpsRepository(CrudRepository):
    def __init__(self):
        super(PushUpsRepository, self).__init__(PushUp)


class RunRepository(CrudRepository):
    def __init__(self):
        super(RunRepository, self).__init__(Run)


class WeightRepository(CrudRepository):
    def __init__(self):
        super(WeightRepository, self).__init__(Weight)


class StatisticsRepository(Repository):
    """
    Repository for calculating statistics. This has been updated to work
    with NDB model objects instead of dictionaries.
    """

    def __init__(self):
        super(StatisticsRepository, self).__init__()

    def running_stats(self, username):
        repository = RunRepository()
        # The 'order' parameter now uses the NDB model property
        items = repository.fetch_by_username(username, order=[-Run.activity_date, -Run.activity_time])
        
        if not items:
            return {}

        count = len(items)
        date_last_run = items[0].activity_date
        days_from_last_run = self._days_from_last_run(date_last_run)

        total_calories = sum(item.calories for item in items if item.calories)
        total_distance = sum(item.distance for item in items if item.distance)
        total_time = sum(item.duration for item in items if item.duration)
        
        # Handle speed calculation, now accessing object properties
        speeds = []
        for item in items:
            if item.speed is not None:
                speeds.append(item.speed)
            elif item.distance is not None and item.duration > 0:
                speeds.append(item.distance / (item.duration / 60.0))
        
        total_speed = sum(speeds)

        return {
            'avg_calories': self._avg(total_calories, count),
            'avg_speed': self._avg(total_speed, len(speeds)) if speeds else 0.0,
            'avg_distance': self._avg(total_distance, count),
            'avg_time': self._avg(total_time, count),
            'count': count,
            'date_last_run': date_last_run,
            'days_from_last_run': days_from_last_run,
            'max_calories': max(item.calories for item in items if item.calories),
            'max_distance': max(item.distance for item in items if item.distance),
            'max_speed': max(speeds) if speeds else 0.0,
            'max_time': max(item.duration for item in items if item.duration),
            'total_distance': total_distance,
            'total_time': total_time,
            'total_calories': total_calories
        }

    def _avg(self, total, count):
        if not count:
            return 0.0
        return float(total) / float(count)

    def _days_from_last_run(self, date_last_run):
        if date_last_run:
            # NDB properties are already date/datetime objects
            diff = abs(datetime.now().date() - date_last_run)
            return diff.days
        return None

    def weighing_stats(self, username):
        repository = WeightRepository()
        # Order using the NDB model property
        items = repository.fetch_by_username(username, order=[-Weight.weighing_date])

        if not items:
            return {}
        
        count = len(items)
        last_weight = items[0].weight
        
        all_weights = [item.weight for item in items if item.weight is not None]
        total = sum(all_weights)
        
        # Calculate stats for the last 20 entries
        last_20_weights = all_weights[:20]
        total_last20 = sum(last_20_weights)
        avg_last20 = self._avg(total_last20, len(last_20_weights))

        return {
            'avg': self._avg(total, len(all_weights)),
            'avg_last20': avg_last20,
            'count': count,
            'growth_rate_last20': self._growth_rate(avg_last20, last_weight),
            'last_weight': last_weight,
            'max': max(all_weights) if all_weights else 0.0,
            'min': min(all_weights) if all_weights else 0.0,
            'trend': '' # This was empty before, keeping it
        }

    def _growth_rate(self, avg, last):
        if not avg or not last:
            return 0.0
        # https://www.wikihow.com/Calculate-Growth-Rate
        return ((float(last) / float(avg)) - 1.0) * 100.0