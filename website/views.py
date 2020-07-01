from uuid import uuid4
import logging
import traceback
from time import time
from datetime import datetime

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import viewsets
from rest_framework import status
from rest_framework import generics
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.schemas import ManualSchema, AutoSchema
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import coreapi
import coreschema

from common.clients import ZBXClient
from common.pagination import StandardPagination
from website.models import Website
from website.serializers import WebsiteSerializer
from website.filters import WebsiteFilter


LOG = logging.getLogger('collie')


class WebsiteViewSet(viewsets.ModelViewSet):
    """
    站点监控视图
    """

    serializer_class = WebsiteSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filter_class = WebsiteFilter

    def get_queryset(self):
        return Website.objects.filter(owner=self.request.user)

    def perform_destroy(self, instance):
        try:
            ZBXClient.item.delete(instance.hc_item_id, instance.lt_item_id,
                                  instance.kw_item_id)
        except Exception as e:
            if 'No permissions to referred object or it does not exist' in str(e):
                instance.delete()
            else:
                LOG.error(f'failed to delete website for user {self.request.user.id} :' + traceback.format_exc())
                raise e

    @action(methods=['get'], detail=True, schema=AutoSchema(manual_fields=[
        coreapi.Field(
            'from',
            required=False,
            location='query',
            schema=coreschema.String(description='开始时间戳, 默认为前60分钟的时间戳')
        ),
        coreapi.Field(
            'to',
            required=False,
            location='query',
            schema=coreschema.String(description='结束时间戳, 默认为当前时间戳')
        )
    ]))
    def availability(self, request, *args, **kwargs):
        """
        网站可用性历史数据
        """
        website = self.get_object()
        now = int(time()//60*60)
        time_from = int(request.GET.get('from', now - 3600))
        if time_from < website.created_at.timestamp()//60*60:
            time_from = website.created_at.timestamp()//60*60
        time_till = int(request.GET.get('to', now))
        params = {
            'objectids': website.trigger_id,
            'time_from': time_from,
            'output': ['clock', 'value'],
            'sortfield': 'clock'
        }
        if time_from:
            params['time_from'] = time_from
        if time_till:
            params['time_till'] = time_till
        events = ZBXClient.event.get(**params)
        if not events:
            problem_events_till = ZBXClient.event.get(objectids=website.trigger_id,
                                                      problem_time_till=now,
                                                      limit=1)
            status = 0 if problem_events_till else 1
            data = [{'time': clock, 'value': status}
                    for clock in range(int(time_from), int(time_till), 180)]
        else:
            data = [{'time': clock}
                    for clock in range(int(time_from), int(time_till), 180)]
            events = [{'time': int(event['clock'])//60*60,
                       'value': int(event['value'])}
                      for event in events][::-1]
            event = None
            for d in data:
                if not event:
                    event = events.pop()
                if d['time'] < event['time']:
                    d['value'] = 0 if event['time'] == 1 else 0
                elif d['time'] == event['time']:
                    d['value'] = event['value']
                    if events:
                        event = None
                #    if not events:
                #        break
                elif not events and d['time'] > event['time']:
                    d['value'] = event['value']
                #    continue
        return Response(data)

    @action(methods=['get'], detail=True, schema=AutoSchema(manual_fields=[
        coreapi.Field(
            'from',
            required=False,
            location='query',
            schema=coreschema.String(description='开始时间戳, 默认为前60分钟的时间戳')
        ),
        coreapi.Field(
            'to',
            required=False,
            location='query',
            schema=coreschema.String(description='结束时间戳, 默认为当前时间戳')
        )
    ]))
    def loadtime(self, request, *args, **kwargs):
        """
        网站加载时间历史数据，单位秒
        """
        time_from = request.GET.get('from', int(time()//60*60) - 3600)
        time_till = request.GET.get('to')
        website = self.get_object()
        params = {
            'itemids': website.lt_item_id,
            'time_from': time_from,
            'history': 0,
            'output': ['clock', 'value']
        }
        if time_till:
            params['time_till'] = time_till
        history = ZBXClient.history.get(**params)
        data_generator = map(lambda x:
                             {
                                 'time': int(x['clock']),
                                 'value': float(x['value'])
                             },
                             history)
        data = [d for d in data_generator]
        return Response(data)

    @action(methods=['get'], detail=False, url_path='problem-count')
    def problem(self, request, *args, **kwargs):
        """
        网站当前告警数
        """

        params = {
            'tags': [{'tag': 'user', 'value': str(request.user.id)}],
            'countOutput': True,
            'filter': {'status': 0, 'value': 1}
        }
        count = ZBXClient.trigger.get(**params)
        return Response({'count': int(count)})
