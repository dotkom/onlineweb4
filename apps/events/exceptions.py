from django.utils import timezone

from .constants import RegisterStatus


class RegisterException(Exception):
    def __init__(
        self, status: RegisterStatus, offset: timezone.timedelta = None,
    ):
        self.status = status
        self.offset = offset
        super().__init__()
