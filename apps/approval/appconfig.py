from django.apps import AppConfig


class ApprovalConfig(AppConfig):
    name = 'apps.approval'
    verbose_name = 'Approval'

    def ready(self):
        super().ready()
        import apps.approval.signals  # flake8: noqa
