from apps.api.utils import SharedAPIRootRouter

from .views import CommitteeApplicationViewSet

urlpatterns = []

# API v1
router = SharedAPIRootRouter()
router.register('committeeapplications', CommitteeApplicationViewSet, base_name='committeeapplications')
