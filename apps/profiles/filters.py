import django_filters
from django.contrib.auth.models import Group

from apps.authentication.models import OnlineUser as User


class ProfileFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="year", method="filter_year")
    group = django_filters.CharFilter(method="filter_group")

    class Meta():
        model = User
        fields = ("year", "group")

    def filter_year(self, queryset, name, value):
        user_ids = [user.id for user in queryset.all() if user.year == value]
        return User.objects.filter(pk__in=user_ids)

    def filter_group(self, queryset, name, value):
        group = Group.objects.filter(name=value)
        return queryset.filter(groups__in=group)
