from oauth2_provider.signals import app_authorized

from apps.sso.models import ApplicationConsent


def handle_app_authorized(sender, request, token, **kwargs):
    if ApplicationConsent.objects.filter(
        pk=token.application.pk, user=token.user
    ).exists():
        return
    if not token.user:
        return

    consent, created = ApplicationConsent.objects.get_or_create(
        user=token.user,
        client=token.application,
        defaults={"approved_scopes": token.scopes},
    )

    if not created:
        consent.approved_scopes = token.scopes
        consent.save()


app_authorized.connect(handle_app_authorized)
