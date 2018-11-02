from apps.api.utils import SharedAPIRootRouter
from apps.contribution import views

urlpatterns = [
]

router = SharedAPIRootRouter()
router.register('repositories', views.RepositoryViewSet)
