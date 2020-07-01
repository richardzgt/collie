from django.conf.urls import url, include
from rest_framework import routers

from dashboard import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'user_settings', views.UserSettingViewSet, basename='user_settings')
router.register(r'history', views.HistoryViewset, basename='history')
router.register(r'config', views.ConfigViewSet, basename='config')

urlpatterns = [
]
urlpatterns += router.urls
