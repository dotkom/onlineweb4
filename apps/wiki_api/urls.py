# API v1
from apps.api.utils import SharedAPIRootRouter
from apps.wiki_api import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register("wiki", views.WikiViewSet, base_name="wiki_api")
