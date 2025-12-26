from eridanus.repository import StatisticsRepository
from eridanus.services import BmiCalculatorService


class DashboardService:
    """Service for aggregating dashboard statistics."""

    def __init__(self, repository=None):
        self.repository = repository or StatisticsRepository()

    def home_stats(self, username):
        running_stats = self.repository.running_stats(username)
        weighing_stats = self.repository.weighing_stats(username)

        # TODO: Height is currently hardcoded to 1.82m.
        # It should be fetched from the user profile in the database.
        # I need a page for user information like height, birth year (to compute age)
        user_height = 1.82

        bmi_calculator = BmiCalculatorService(
            weighing_stats['last_weight'],
            user_height)
        desired_weight = bmi_calculator.calculate_desired_weight(BmiCalculatorService.TARGET_BMI_NORMAL)
        return {
            'bmi': {
                'bmi': bmi_calculator.bmi,
                'status': bmi_calculator.status,
            },
            'activities': {
                'running': running_stats
            },
            'weighing': weighing_stats,
            'objectives': {
                'weight': desired_weight
            }
        }


    # def get_day_from_last_run_class(self):
    #     if self.days_past_from_last_run is None:
    #         return ''
    #     diff = self.days_past_from_last_run
    #     if diff < 3:
    #         return 'label-success'
    #     elif diff < 4:
    #         return 'label-warning'
    #     else:
    #         return 'label-danger'
