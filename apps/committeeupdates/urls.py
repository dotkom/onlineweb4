from apps.api.utils import SharedAPIRootRouter
from apps.committeeupdates import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register("committeeupdates", views.CommitteeUpdateViewSet)