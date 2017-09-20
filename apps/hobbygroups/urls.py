from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.hobbygroups import views

urlpatterns = [
    url(r'^$', views.index, name='hobbygroups_index'),
]

router = SharedAPIRootRouter()
router.register('hobbys', views.HobbyViewSet)
