from apps.api.utils import SharedAPIRootRouter
from apps.notifications import views

urlpatterns = []

router = SharedAPIRootRouter()

router.register(
    prefix="notifications/subscriptions",
    viewset=views.SubscriptionViewSet,
    basename="notifications_subscriptions",
)
router.register(
    prefix="notifications/messages",
    viewset=views.NotificationViewSet,
    basename="notifications_messages",
)
router.register(
    prefix="notifications/permissions",
    viewset=views.PermissionViewSet,
    basename="notifications_permissions",
)
router.register(
    prefix="notifications/user-permissions",
    viewset=views.UserPermissionViewSet,
    basename="notifications_user_permissions",
)
