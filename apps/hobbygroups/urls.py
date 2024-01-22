from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.hobbygroups import views

urlpatterns = [re_path(r"^$", views.index, name="hobbygroups_index")]

router = SharedAPIRootRouter()
router.register("hobbys", views.HobbyViewSet)
