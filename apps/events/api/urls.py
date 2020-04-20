from apps.api.utils import SharedAPIRootRouter
from apps.events.api import views

urlpatterns = []

# API v1
router = SharedAPIRootRouter()
router.register("event/attendees", views.AttendeeViewSet, basename="events_attendees")
router.register("event/events", views.EventViewSet, basename="events_events")
router.register(
    "event/attendance-events",
    views.AttendanceEventViewSet,
    basename="events_attendance_events",
)
router.register("event/extras", views.ExtrasViewSet, basename="events_extras")
router.register(
    "event/rule-bundles", views.RuleBundleViewSet, basename="events_rule_bundles"
)
router.register(
    "event/field-of-study-rules",
    views.FieldOfStudyRuleViewSet,
    basename="events_field_of_study_rules",
)
router.register(
    "event/grade-rules", views.GradeRuleViewSet, basename="events_grade_rules"
)
router.register(
    "event/user-group-rules",
    views.UserGroupRuleViewSet,
    basename="events_user_group_rules",
)
