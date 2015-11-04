from rest_framework.routers import DefaultRouter, SimpleRouter


class SharedAPIRootRouter(SimpleRouter):
    shared_router = DefaultRouter()

    def register(self, *args, **kwargs):
        self.shared_router.register(*args, **kwargs)
        # super().register(*args, **kwargs)  # Python 3 way of calling super method
        super(SimpleRouter, self).register(*args, **kwargs)  # Python 2 way of calling super method
