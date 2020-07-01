#!/usr/bin/env python

from django.conf.urls import url, include
from configure import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'host', views.HostViewSet, basename='host')
router.register(r'trigger', views.TriggerViewSet, basename='trigger')
router.register(r'item', views.ItemViewSet, basename='item')
router.register(r'template', views.TemplateViewSet, basename='template')
router.register(r'application', views.ApplicationViewSet, basename='application')

urlpatterns = [
    # url(r'^template$', views.Template.as_view(), name='template'),
] + router.urls
