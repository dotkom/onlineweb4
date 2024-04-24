from apps.api.utils import SharedAPIRootRouter
from apps.authentication.api import views as api_views

# Our url-setup is wack, since this is now API-only, we need a dummy-urlpattern to import this file _somewhere_
urlpatterns = []

# API v1
router = SharedAPIRootRouter()
router.register("users", api_views.UserViewSet, basename="users")
router.register(
    "user/permissions", api_views.PermissionsViewSet, basename="user_permissions"
)
router.register("user/positions", api_views.PositionViewSet, basename="user_positions")
router.register(
    "user/special-positions",
    api_views.SpecialPositionViewSet,
    basename="user_special_positions",
)
router.register("groups", api_views.GroupViewSet, basename="groups")
router.register(
    "group/online-groups", api_views.OnlineGroupViewSet, basename="online_groups"
)
router.register("group/roles", api_views.GroupRoleViewSet, basename="group_roles")
