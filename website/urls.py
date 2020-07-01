from django.conf.urls import url, include
from rest_framework import routers

from website import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'website', views.WebsiteViewSet, basename='website')

urlpatterns = [
]
urlpatterns += router.urls
