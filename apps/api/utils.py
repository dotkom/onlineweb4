from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.schemas.openapi import AutoSchema


class SharedAPIRootRouter(SimpleRouter):
    shared_router = DefaultRouter()

    def register(self, *args, **kwargs):
        self.shared_router.register(*args, **kwargs)
        super().register(*args, **kwargs)


class PrefixRemovedAutoSchema(AutoSchema):
    """
    This class overrides AutoSchema to remove the `api/v1`-prefix of our routes.
    Tags are used to sort endpoints in the Swagger-docs.

    To override tags in a single view, import AutoSchema and set schema=AutoSchema(tags=["tag1"]).

    Example:
        from rest_framework.schemas.openapi import AutoSchema

        class EventViewSet(viewsets.ModelViewSet):
            schema = AutoSchema(tags=["event"])

    To override tags in multiple views, import AutoSchema and subclass it with a get_tags-method like in this class.

    Example:
        from rest_framework.schemas.openapi import AutoSchema

        class CommitteeApplicationSchema(AutoSchema):
            def get_tags(self, path, method):
                # Method is choice of POST, GET, PATCH, etc. as strings
                # Path is URL starting at with '/api/'
            return ["CommitteeApplication"]

    """

    def get_tags(self, path, method):
        pathTopic = path.split("/")[3]
        return [pathTopic.capitalize()]
