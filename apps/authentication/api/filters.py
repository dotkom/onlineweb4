import django_filters
from watson import search as watson_search

from ..models import GroupMember, OnlineGroup, OnlineUser


class UserFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method="watson_filter")

    def watson_filter(self, queryset, name, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset

    class Meta:
        model = OnlineUser
        fields = ("first_name", "last_name", "rfid", "query")


# This is a filter for finding which groups an user is a member of
def filter_member_user(_, __, value):
    members = GroupMember.objects.filter(user=value)
    return OnlineGroup.objects.filter(members__in=members)


class OnlineGroupFilter(django_filters.FilterSet):
    members__user = django_filters.ModelChoiceFilter(
        queryset=OnlineUser.objects.all(), method=filter_member_user
    )
