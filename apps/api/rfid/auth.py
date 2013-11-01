from tastypie.authentication import Authentication

class RfidAuthentication(Authentication):
    """
    This custom authentication model is used only for the RFID app, allowing a static API KEY
    to be used to authenticate, ant then using a NOOP authorization to allow user and attendee patching
    """

    def is_authenticated(self, request, **kwargs):
        if '5db1fee4b5703808c48078a76768b155b421b210c0761cd6a5d223f4d99f1eaa' in request.api_key:
            return True
        return False

    def get_identifier(self, request):
        return 'RFID-APP'
