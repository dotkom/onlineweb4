from django.urls import path, re_path

from apps.api.utils import SharedAPIRootRouter
from apps.marks.views import MarksViewSet, SuspensionViewSet
from apps.profiles import views

urlpatterns = [
    re_path(r"^$", views.index, name="profiles"),
    # Show a specific profile.
    path(
        "view/<int:pk>/",
        views.view_profile,
        name="profiles_view",
    ),
    re_path(r"^feedback-pending/$", views.feedback_pending, name="feedback_pending"),
    re_path(r"^edit/$", views.edit_profile, name="profile_edit"),
    re_path(r"^privacy/$", views.privacy, name="profile_privacy"),
    re_path(r"^position/$", views.position, name="profile_position"),
    re_path(
        r"^create_gsuite/$",
        views.GSuiteCreateAccount.as_view(),
        name="profile_create_gsuite_account",
    ),
    re_path(
        r"^reset_gsuite/$",
        views.GSuiteResetPassword.as_view(),
        name="profile_reset_gsuite_account",
    ),
    # Ajax views
    re_path(
        r"^deleteposition/$", views.delete_position, name="profile_delete_position"
    ),
    re_path(
        r"^email/toggle_infomail/$",
        views.toggle_infomail,
        name="profile_toggle_infomail",
    ),
    re_path(
        r"^email/toggle_jobmail/$", views.toggle_jobmail, name="profile_toggle_jobmail"
    ),
    re_path(
        r"^marks/update_mark_rules/$",
        views.update_mark_rules,
        name="profile_update_mark_rules",
    ),
    # Endpoint that exposes a json lump of all users but only id and name. Only used for autocomplete in the dashboard
    re_path(
        r"^api_plain_user_search/$",
        views.api_plain_user_search,
        name="profiles_api_plain_user_search",
    ),
    # Profile index with active tab.
    re_path(r"^(?P<active_tab>\w+)/$", views.index, name="profiles_active"),
]

router = SharedAPIRootRouter()
router.register(
    "profile/search", views.PublicProfileSearchSet, basename="profile-search"
)
router.register(
    "profile/privacy", views.PersonalPrivacyView, basename="profile-privacy"
)
router.register("profile/marks", MarksViewSet, basename="profile-marks")
router.register(
    "profile/suspensions", SuspensionViewSet, basename="profile-suspensions"
)
router.register("profile", views.ProfileViewSet, basename="profile")
