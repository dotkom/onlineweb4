from apps.api.utils import SharedAPIRootRouter
from apps.slack import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register("slack", views.InviteViewSet, basename="slack")
