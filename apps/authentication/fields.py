from rest_framework import serializers

from apps.authentication.models import Email


class OnlineUserEmailValidator(object):
    def validate_email(self, email):
        all_emails = [email_obj.email for email_obj in Email.objects.all()]
        if email in all_emails:
            raise serializers.ValidationError(
                "Det eksisterer allerede en bruker med denne e-postadressen"
            )
        return email

    def __call__(self, value):
        return self.validate_email(value)


class OnlineUserEmailField(serializers.EmailField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validator = OnlineUserEmailValidator()
        self.validators.append(validator)
