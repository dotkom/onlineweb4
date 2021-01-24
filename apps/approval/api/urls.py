from apps.api.utils import SharedAPIRootRouter

from .views import (
    CommitteeApplicationPeriodViewSet,
    CommitteeApplicationViewSet,
    MembershipApprovalViewSet,
)

urlpatterns = []

# API v1
router = SharedAPIRootRouter()
router.register(
    "committeeapplications",
    CommitteeApplicationViewSet,
    basename="committeeapplications",
)
router.register(
    "committee-application-periods",
    CommitteeApplicationPeriodViewSet,
    basename="committee-application-periods",
)
router.register(
    "membership-approval", MembershipApprovalViewSet, basename="membership-approval"
)
