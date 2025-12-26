from abc import ABCMeta, abstractmethod
# import warnings


class CrudService(metaclass=ABCMeta):

    @abstractmethod
    def fetch_all(self, username):
        raise NotImplementedError

    @abstractmethod
    def create(self, activity):
        raise NotImplementedError

    @abstractmethod
    def read(self, activity_id):
        raise NotImplementedError

    @abstractmethod
    def update(self, activity):
        raise NotImplementedError

    @abstractmethod
    def delete(self, activity_id):
        raise NotImplementedError


class BmiCalculatorService:

    UNDERWEIGHT = "Underweight"
    NORMAL = "Normal"
    OVERWEIGHT = "Overweight"
    OBESE = "Obese"

    THRESHOLD_UNDERWEIGHT = 18.5
    THRESHOLD_NORMAL = 25.0
    THRESHOLD_OVERWEIGHT = 30.0
    TARGET_BMI_NORMAL = 24.9

    def __init__(self, weight, height):
        if weight is None:
            self.weight = 0.0
        else:
            self.weight = float(weight)

        if height is None:
            self.height = 0.0
        else:
            self.height = float(height)
        self.bmi = self._calculate_bmi()
        self.status = self._get_status()

    def _calculate_bmi(self):
        '''
        weight (kg)
        height (m)
        '''
        if self.height == 0.0:
            return 0.0

        return self.weight / (self.height ** 2)

    def calculate_desired_weight(self, bmi):
        return float(bmi) * (self.height ** 2)

    def _get_status(self):
        if self.bmi < self.THRESHOLD_UNDERWEIGHT:
            return BmiCalculatorService.UNDERWEIGHT
        elif self.bmi < self.THRESHOLD_NORMAL:
            return BmiCalculatorService.NORMAL
        elif self.bmi < self.THRESHOLD_OVERWEIGHT:
            return BmiCalculatorService.OVERWEIGHT
        else:
            return BmiCalculatorService.OBESE