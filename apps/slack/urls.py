from apps.api.utils import SharedAPIRootRouter
from apps.slack import views
from apps.shop.views import InventoryViewSet

urlpatterns = []

router = SharedAPIRootRouter()
router.register('slack', views.InviteViewSet, base_name='slack')
