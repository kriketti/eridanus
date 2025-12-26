import logging

from datetime import datetime, date, time

from eridanus.models import Crunch, Run, Weight, PushUp
from eridanus.utils.format import format_date

from google.cloud import datastore
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Repository(object):
    def __init__(self):
        self.client = datastore.Client()

class CrudRepository(Repository):

    def __init__(self, kind):
        super(CrudRepository, self).__init__()
        self.kind = kind

    def query(self):
        return self.client.query(kind=self.kind)

    def _key(self, identifier=None) -> datastore.Key:
        if not identifier:
            return self.client.key(self.kind)
        # Dacă identificatorul este un string numeric, îl convertim în int (ID)
        if isinstance(identifier, str) and identifier.isdigit():
            return self.client.key(self.kind, int(identifier))
        return self.client.key(self.kind, identifier)

    def _sanitize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in record.items():
            if isinstance(value, date) and not isinstance(value, datetime):
                record[key] = datetime.combine(value, datetime.min.time())
            elif isinstance(value, time):
                record[key] = datetime.combine(date(1970, 1, 1), value)
        return record

    def create(self, record):
        logger.debug(f'Creating record of kind {self.kind}: {record}')
        # https://cloud.google.com/datastore/docs/concepts/entities
        record = self._sanitize_record(record)
        with self.client.transaction():
            record['creation_datetime'] = datetime.now()
            incomplete_key = self._key()
            entity = datastore.Entity(key=incomplete_key)
            entity.update(record)
            self.client.put(entity)
        return None

    def delete(self, identifier):
        # https://cloud.google.com/datastore/docs/concepts/entities
        key = self._key(identifier)
        if key:
            return self.client.delete(key)
        else:
            pass
            # TODO: logg or throw an error

    def fetch_all(self):
        ''' fetch data from data store '''
        query = self.query()
        query.order = ['-activity_date']
        return query.fetch()

    def fetch_by_username(self, username, order=None):
        ''' fetch data from data store '''
        query = self.query()
        query.add_filter('usernickname', '=', username)
        if order:
            query.order = order
        return query.fetch()

    def read(self, identifier):
        key = self._key(identifier)
        return self.client.get(key)

    def update(self, record):
        activity = None
        record = self._sanitize_record(record)
        with self.client.transaction():
            # Folosim 'id' sau 'urlsafe' pentru compatibilitate temporară, dar preferăm id
            identifier = record.get('id') or record.get('urlsafe')
            activity = self.read(identifier)
            if activity:
                for key in record.keys():
                    if key in ['urlsafe', 'id']:
                        continue
                    if key in activity:
                        activity[key] = record[key]
                self.client.put(activity)
        return activity


class CrunchesRepository(CrudRepository):
    def __init__(self):
        super(CrunchesRepository, self).__init__(kind='Crunch')


class JumpRopeRepository(CrudRepository):
    def __init__(self):
        super(JumpRopeRepository, self).__init__(kind='JumpRope')


class PushUpsRepository(CrudRepository):
    def __init__(self):
        super(PushUpsRepository, self).__init__(kind='PushUp')


class RunRepository(CrudRepository):
    def __init__(self):
        super(RunRepository, self).__init__(kind='Run')


class WeightRepository(CrudRepository):
    def __init__(self):
        super(WeightRepository, self).__init__(kind='Weight')


class StatisticsRepository(Repository):

    def __init__(self):
        super(StatisticsRepository, self).__init__()

    def running_stats(self, username):
        avg_calories = 0
        avg_speed = 0.0
        avg_distance = 0.0
        avg_time = 0
        count = 0
        date_last_run: datetime = datetime.min
        days_from_last_run = 0
        max_calories = 0
        max_distance = 0
        max_speed = 0.0
        max_time = 0
        total_calories = 0
        total_distance = 0
        total_time = 0
        total_speed = 0.0


        repository = RunRepository()
        items = repository.fetch_by_username(username)
        count = 0
        for item in items:
            if count == 0:
                date_last_run = item['activity_date']
                days_from_last_run = self._days_from_last_run(
                    date_last_run)
            count = count + 1
            duration = item['duration']
            if item['calories']:
                total_calories += item['calories']
                if item['calories'] > max_calories:
                    max_calories = item['calories']
            total_distance += item['distance']
            total_time += duration
            if item['distance'] > max_distance:
                max_distance = item['distance']
            if duration > max_time:
                max_time = duration
            speed = item['speed']
            if item['speed'] is None:
                speed = item['distance'] / (duration / 60.0)
            total_speed += speed
            if speed > max_speed:
                max_speed = speed
        if count > 0:
            avg_calories = self._avg(total_calories, count)
            avg_distance = self._avg(total_distance, count)
            avg_time = self._avg(total_time, count)
            avg_speed = self._avg(total_speed, count)
        return {
            'avg_calories': avg_calories,
            'avg_speed': avg_speed,
            'avg_distance': avg_distance,
            'avg_time': avg_time,
            'count': count,
            'date_last_run': datetime.date(date_last_run),
            'days_from_last_run': days_from_last_run,
            'max_calories': max_calories,
            'max_distance': max_distance,
            'max_speed': max_speed,
            'max_time': max_time,
            'total_distance': total_distance,
            'total_time': total_time,
            'total_calories': total_calories
        }

    def _avg(self, total, count):
        return float(total)/float(count)

    def _days_from_last_run(self, date_last_run):
        logger.debug(date_last_run)
        if date_last_run:
            diff = abs(datetime.now().date() - date_last_run.date())
            return diff.days
        return None

    def weighing_stats(self, username):
        avg = 0.0
        avg_last20 = 0.0
        count = 0
        growth_rate_last20 = 0.0
        last_weight = 0.0
        min = 0.0
        max = 0.0
        trend = ''
        total = 0.0
        total_last20 = 0.0

        repository = WeightRepository()
        items = repository.fetch_by_username(username)
        count = 0
        for item in items:
            if count == 0:
                last_weight = item['weight']
            count = count + 1
            weight = item['weight']
            total += weight
            if min > weight:
                min = weight
            if max < weight:
                max = weight
            if count <= 19:
                total_last20 = total
        if count > 0:
            avg_last20 = self._avg(
                total_last20,
                20.0 if count > 20 else float(count))
            avg = self._avg(total, count)
        if count > 1:
            growth_rate_last20 = self._growth_rate(avg_last20, last_weight)
        return {
            'avg': avg,
            'avg_last20': avg_last20,
            'count': count,
            'growth_rate_last20': growth_rate_last20,
            'last_weight': last_weight,
            'max': max,
            'min': min,
            'trend': trend
        }

    def _growth_rate(self, avg, last):
        # https://www.wikihow.com/Calculate-Growth-Rate
        return ((float(last) / float(avg)) - 1.0) * 100.0
