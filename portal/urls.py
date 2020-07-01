#!/usr/bin/env python

from django.conf.urls import url, include
from rest_framework import routers

from portal import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'user', views.UserViewSet)

urlpatterns = [
    url(r'^login$', views.ObtainJSONWebToken.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout')
]
urlpatterns += router.urls
