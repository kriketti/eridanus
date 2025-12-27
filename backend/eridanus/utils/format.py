from eridanus.constants import ERIDANUS_DATE_FORMAT, ERIDANUS_TIME_FORMAT
from datetime import datetime, date, time


def format_date(date_value: date) -> str:
    return date_value.strftime(ERIDANUS_DATE_FORMAT)


def format_time(time_value: time) -> str:
    return time_value.strftime(ERIDANUS_TIME_FORMAT)


def to_date(date_value: str, format: str) -> date:
    return datetime.strptime(date_value, format).date()


def to_time(time_value: str, format: str='%H:%M') -> time:
    return datetime.strptime(time_value, format).time()


def to_datetime(datetime_value: str, format: str) -> datetime:
    return datetime.strptime(datetime_value, format)


def date_to_datetime(form_date: date) -> datetime:
    '''
    Google Datastore Client doesn't support the serialization of datetime.date objects
    
    :param form_date: Date object that must converted into datetie
    :type form_date: date
    :return: The datetime object
    :rtype: datetime
    '''
    return datetime.combine(form_date, datetime.min.time())


def time_to_datetime(form_time: time) -> datetime:
    '''
    Google Datastore Client doesn't support the serialization of datetime.time objects

    :param form_time: Time object that must converted into datetime
    :type form_time: time
    :return: The datetime object
    :rtype: datetime
    '''
    return datetime.combine(date(1970, 1, 1), form_time)