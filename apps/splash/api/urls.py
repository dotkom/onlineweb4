from apps.api.utils import SharedAPIRootRouter
from apps.splash.api.views import SplashEventViewSet

urlpatterns = []

router = SharedAPIRootRouter()
router.register("splash-events", SplashEventViewSet)
