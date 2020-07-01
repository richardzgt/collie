from django.conf.urls import url, include
from rest_framework import routers

from report import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'website', views.WebsiteReportViewSet, basename='website-report')
router.register(r'host', views.WebsiteReportViewSet, basename='host-report')

urlpatterns = [
]
urlpatterns += router.urls
