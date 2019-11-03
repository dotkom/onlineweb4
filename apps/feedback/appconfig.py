from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    name = "apps.feedback"
    verbose_name = "Feedback"

    def ready(self):
        super(FeedbackConfig, self).ready()

        from reversion import revisions as reversion

        from apps.feedback.models import (
            FieldOfStudyAnswer,
            MultipleChoiceAnswer,
            RatingAnswer,
            RegisterToken,
            TextAnswer,
        )

        reversion.register(FieldOfStudyAnswer)
        reversion.register(MultipleChoiceAnswer)
        reversion.register(RatingAnswer)
        reversion.register(RegisterToken)
        reversion.register(TextAnswer)
