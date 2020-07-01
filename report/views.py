from uuid import uuid4
import logging
import traceback
from time import time
from datetime import datetime

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from rest_framework import status
from rest_framework import generics
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.schemas import ManualSchema, AutoSchema
import coreapi
import coreschema

from common.clients import ZBXClient
from common.pagination import StandardPagination
from website.models import Website
from website.serializers import WebsiteSerializer


LOG = logging.getLogger('collie')


class WebsiteReportViewSet(viewsets.ViewSet):

    def list(self, request):
        triggers = ZBXClient.trigger.get(groupids=19,
                                         expandDescription='1',
                                         output=['description'])
        problems = ZBXClient.problem.get(groupids=19,
                                         output=['objectid', 'clock', 'r_clock'])
        return Response(triggers)


class HostReportViewSet(viewsets.ViewSet):

    def list(self, request):
        triggers = ZBXClient.trigger.get(groupids=19,
                                         expandDescription='1',
                                         output=['description'])
        problems = ZBXClient.problem.get(groupids=19,
                                         output=['objectid', 'clock', 'r_clock'])
        return Response(triggers)
