import django_filters

from website.models import Website

class WebsiteFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    url = django_filters.CharFilter(lookup_expr='icontains')
    enabled = django_filters.BooleanFilter()

    class Meta:
        model = Website
        fields = ['name', 'url', 'enabled']
