from apps.api.utils import SharedAPIRootRouter
from apps.notifications import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register(
    prefix='notifications/settings',
    viewset=views.NotificationSettingsViewSet,
    base_name='notifications-settings',
)
router.register(
    prefix='notifications/subscriptions',
    viewset=views.NotificationSubscriptionViewSet,
    base_name='notifications-subscriptions',
)
