import django_filters as filters

from ..models import CommitteeApplicationPeriod


class CommitteeApplicationPeriodFilter(filters.FilterSet):
    accepting_applications = filters.BooleanFilter(field_name="accepting_applications")
    actual_deadline__lte = filters.DateTimeFilter(
        field_name="actual_deadline", lookup_expr="lte"
    )
    actual_deadline__gte = filters.DateTimeFilter(
        field_name="actual_deadline", lookup_expr="lte"
    )

    class Meta:
        model = CommitteeApplicationPeriod
        fields = {
            "start": ["gte", "lte"],
            "deadline": ["gte", "lte"],
            "accepting_applications": "exact",
            "actual_deadline__lte": "exact",
            "actual_deadline__gte": "exact",
        }
