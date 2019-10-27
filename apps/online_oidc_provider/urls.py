from apps.api.utils import SharedAPIRootRouter

from . import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register("oidc/consent", views.UserConsentViewSet, basename="oidc_user_consent")
router.register("oidc/clients", views.ClientViewSet, basename="oidc_clients")
router.register(
    "oidc/response-types", views.ResponseTypeViewSet, basename="oidc_response_types"
)
