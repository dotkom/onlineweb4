from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.mailinglists import views

urlpatterns = [re_path(r"^$", views.index, name="mailinglists_index")]


router = SharedAPIRootRouter()
router.register(
    "mailinglists/groups", views.MailGroupViewSet, basename="mailinglists_groups"
)
router.register(
    "mailinglists/entities", views.MailEntityViewSet, basename="mailinglists_entities"
)
