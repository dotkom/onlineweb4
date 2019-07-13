from apps.api.utils import SharedAPIRootRouter
from apps.notifications import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register(
    prefix='notifications/settings',
    viewset=views.NotificationSettingsViewSet,
    base_name='notifications_settings',
)
router.register(
    prefix='notifications/subscriptions',
    viewset=views.NotificationSubscriptionViewSet,
    base_name='notifications_subscriptions',
)
router.register(
    prefix='notifications/messages',
    viewset=views.NotificationViewSet,
    base_name='notifications_messages'
)
