from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.contribution import views

urlpatterns = [
    url(r'^$', views.index, name='contribution_index'),
]

router = SharedAPIRootRouter()
router.register('repositories', views.RepositoryViewSet)
