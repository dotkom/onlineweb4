from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    name = "apps.feedback"
    verbose_name = "Feedback"

    def ready(self):
        super().ready()

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

        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.feedback.signals  # noqa: F401
