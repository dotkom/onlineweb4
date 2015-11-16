from django.apps import AppConfig

import reversion


class FeedbackConfig(AppConfig):
    name = 'apps.feedback'
    verbose_name = 'Feedback'

    def ready(self):
        super(FeedbackConfig, self).ready()

        from apps.feedback.models import (
            FieldOfStudyAnswer, MultipleChoiceAnswer, RatingAnswer, RegisterToken, TextAnswer)

        reversion.register(FieldOfStudyAnswer)
        reversion.register(MultipleChoiceAnswer)
        reversion.register(RatingAnswer)
        reversion.register(RegisterToken)
        reversion.register(TextAnswer)
