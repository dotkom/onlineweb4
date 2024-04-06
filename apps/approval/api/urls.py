from apps.api.utils import SharedAPIRootRouter

from .views import MembershipApprovalViewSet

urlpatterns = []

# API v1
router = SharedAPIRootRouter()
router.register(
    "membership-application",
    MembershipApprovalViewSet,
    basename="membership-application",
)
