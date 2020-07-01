from django.conf.urls import url, include
from rest_framework import routers

from event import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'host', views.HostEventViewSet, basename='host-event')
router.register(r'website', views.WebsiteEventViewSet, basename='website-event')

urlpatterns = [
]
urlpatterns += router.urls
