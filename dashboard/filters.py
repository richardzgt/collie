import django_filters
from django.db.models import Q
from dashboard.models import Config


class ConfigFilter(django_filters.FilterSet):
    user_id = django_filters.CharFilter(method='search_user')

    def search_user(self, queryset, status, value):
        return queryset.filter(Q(user__id=value))

    class Meta:
        model = Config
        fields = ['user_id']
