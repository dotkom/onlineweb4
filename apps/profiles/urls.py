# -*- encoding: utf-8 -*-

from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.marks.views import MarksViewSet, SuspensionViewSet
from apps.profiles import views
from apps.shop.views import UserOrderViewSet

urlpatterns = [
    re_path(r"^$", views.index, name="profiles"),
    # Show a specific profile.
    re_path(
        r"^view/(?P<username>[a-zA-Z0-9_-]+)/$",
        views.view_profile,
        name="profiles_view",
    ),
    re_path(r"^feedback-pending/$", views.feedback_pending, name="feedback_pending"),
    re_path(r"^edit/$", views.edit_profile, name="profile_edit"),
    re_path(r"^privacy/$", views.privacy, name="profile_privacy"),
    re_path(r"^connected_apps/$", views.connected_apps, name="profile_connected_apps"),
    re_path(r"^password/$", views.password, name="profile_password"),
    re_path(r"^position/$", views.position, name="profile_position"),
    re_path(r"^email/$", views.add_email, name="profile_add_email"),
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
    # re_path('^internal_services/$', views.internal_services, name='profile_internal_services'),
    # Ajax views
    re_path(
        r"^deleteposition/$", views.delete_position, name="profile_delete_position"
    ),
    re_path(r"^email/delete_email/$", views.delete_email, name="profile_delete_email"),
    re_path(r"^email/set_primary/$", views.set_primary, name="profile_set_primary"),
    re_path(r"^email/verify_email/$", views.verify_email, name="profile_verify_email"),
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
    # Endpoint that exposes a json lump of all users but only id and name.
    re_path(
        r"^api_plain_user_search/$",
        views.api_plain_user_search,
        name="profiles_api_plain_user_search",
    ),
    # Endpoint that exposes a json lump of all users which have set their profile to public.
    re_path(
        "^api_user_search/$", views.api_user_search, name="profiles_api_user_search"
    ),
    re_path(r"^user_search/$", views.user_search, name="profiles_user_search"),
    # Profile index with active tab.
    re_path(r"^(?P<active_tab>\w+)/$", views.index, name="profiles_active"),
]

router = SharedAPIRootRouter()
router.register(
    "profile/search", views.PublicProfileSearchSet, basename="profile-search"
)
router.register("profile/orders", UserOrderViewSet, basename="profile-orders")
router.register(
    "profile/privacy", views.PersonalPrivacyView, basename="profile-privacy"
)
router.register("profile/marks", MarksViewSet, basename="profile-marks")
router.register(
    "profile/suspensions", SuspensionViewSet, basename="profile-suspensions"
)
router.register(
    "profile/emails", views.UserEmailAddressesViewSet, basename="profile-emails"
)
router.register("profile", views.ProfileViewSet, basename="profile")
