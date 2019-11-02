from apps.api.utils import SharedAPIRootRouter
from apps.splash.api.views import AudienceGroupViewSet, SplashEventViewSet

urlpatterns = []

router = SharedAPIRootRouter()
router.register("splash/events", SplashEventViewSet, basename="splash_events")
router.register(
    "splash/audience-groups", AudienceGroupViewSet, basename="splash_audience"
)
