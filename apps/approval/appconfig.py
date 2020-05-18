from django.apps import AppConfig


class ApprovalConfig(AppConfig):
    name = "apps.approval"
    verbose_name = "Approval"

    def ready(self):
        super().ready()
        # noinspection PyUnresolvedReferences
        import apps.approval.signals  # noqa: F401
