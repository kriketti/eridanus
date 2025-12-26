import logging

from eridanus.repository import WeightRepository
from ..services import CrudService
from ..utils.format import format_date

logger = logging.getLogger(__name__)

class WeighingService(CrudService):

    def __init__(self):
        self.repository = WeightRepository()

    def fetch_all(self, username):
        min_weight = None
        items = []
        models = self.repository.fetch_by_username(username, order = ['-weighing_date'])
        for model in models:
            if min_weight is None or min_weight > model['weight']:
                min_weight = model['weight']
            items.append(
                {
                    'id': model.key.id,
                    'weight': model['weight'],
                    'weighing_date': format_date(model['weighing_date'])
                })
        return {'items': items, 'min_weight': min_weight}

    def create(self, weighing):
        return self.repository.create(weighing)

    def read(self, id):
        return self.repository.read(id)

    def update(self, weighing):
        return self.repository.update(weighing)

    def delete(self, id):
        return self.repository.delete(id)
