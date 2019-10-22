from django_filters import filters, filterset


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class TagsFilterMixin:
    tags = filters.CharFilter(field_name='tags__name')
    tags__in = CharInFilter(field_name='tags__name', lookup_expr='in')


class AlbumFilter(filterset.FilterSet, TagsFilterMixin):
    published_date__lte = filters.DateTimeFilter(field_name='published_date', lookup_expr='lte')
    published_date__gte = filters.DateTimeFilter(field_name='published_date', lookup_expr='gte')
    public = filters.BooleanFilter(field_name='public')


class PhotoFilter(filterset.FilterSet, TagsFilterMixin):
    created_date__lte = filters.DateTimeFilter(field_name='created_date', lookup_expr='lte')
    created_date__gte = filters.DateTimeFilter(field_name='created_date', lookup_expr='gte')
    album = filters.NumberFilter(field_name='album')
    photographer = filters.NumberFilter(field_name='photographer')


class UserTagFilter(filterset.FilterSet):
    created_date__lte = filters.DateTimeFilter(field_name='created_date', lookup_expr='lte')
    created_date__gte = filters.DateTimeFilter(field_name='created_date', lookup_expr='gte')
    user = filters.NumberFilter(field_name='user')
    album = filters.NumberFilter(field_name='photo__album')
