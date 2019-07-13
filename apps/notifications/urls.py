from apps.api.utils import SharedAPIRootRouter
from apps.notifications import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register(
    prefix='notifications/settings',
    viewset=views.NotificationSettingsViewSet,
    basename='notifications_settings',
)
router.register(
    prefix='notifications/subscriptions',
    viewset=views.NotificationSubscriptionViewSet,
    basename='notifications_subscriptions',
)
router.register(
    prefix='notifications/messages',
    viewset=views.NotificationViewSet,
    basename='notifications_messages'
)
