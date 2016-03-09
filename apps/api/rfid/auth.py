from django.conf import settings
from tastypie.authentication import Authentication


class RfidAuthentication(Authentication):
    """
    This custom authentication model is used only for the RFID app, allowing a static API KEY
    to be used to authenticate, ant then using a NOOP authorization to allow user and attendee patching
    """

    def is_authenticated(self, request, **kwargs):
        if 'api_key' in request.GET:
            if settings.RFID_API_KEY in request.GET["api_key"]:
                return True
        return False

    def get_identifier(self, request):
        return 'RFID-APP'
