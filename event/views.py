from uuid import uuid4
import logging
import traceback

from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from rest_framework import status
from rest_framework import generics
from rest_framework import mixins
from rest_framework.schemas import ManualSchema
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.utils.urls import replace_query_param
import coreapi
import coreschema

from common.clients import ZBXClient
from portal.models import User
from website.models import Website


LOG = logging.getLogger('collie')


class HostEventViewSet(viewsets.ViewSet):
    """
    主机告警事件视图
    """

    schema = ManualSchema(fields=[
        coreapi.Field(
            'pageNo',
            required=False,
            location='query',
            schema=coreschema.String(
                description='页码',
                pattern=r'\d+'
            )
        ),
        coreapi.Field(
            'pageSize',
            required=False,
            location='query',
            schema=coreschema.String(
                description='分页大小',
                pattern=r'\d+'
            )
        ),
        coreapi.Field(
            'hostid',
            required=False,
            location='query',
            schema=coreschema.String(
                description='主机ID, 如10084',
                pattern=r'\d+'
            )
        ),
        coreapi.Field(
            'from',
            required=False,
            location='query',
            schema=coreschema.String(
                description='Unix timestamp like 1587091000000',
                pattern=r'\d{13}'
            )
        ),
        coreapi.Field(
            'to',
            required=False,
            location="query",
            schema=coreschema.String(
                description='Unix timestamp like 1587091000000',
                pattern=r'\d{13}'
            )
        )
    ], description='查询主机告警事件')

    def list(self, request, *args, **kwargs):
        hostgroupid = User.objects.get(id=request.user.id).zbx_gid
        page = int(request.GET.get('pageNo', 1))
        page_size = int(request.GET.get('pageSize', 10))
        time_from = request.GET.get('from', None)
        time_till = request.GET.get('to', None)
        hostid = request.GET.get('hostid', None)
        url = request.build_absolute_uri()
        data = []
        params = {
            'groupids': hostgroupid,
            'selectHosts': 'extend',
            'select_alerts': 'extend',
            'selectRelatedObject': 'extend',
            'limit': 500
        }

        if time_from:
            params['time_from'] = time_from
        if time_till:
            params['time_till'] = time_till
        if hostid:
            params['hostids'] = hostid
        event_list = ZBXClient.event.get(**params)
        for event in event_list[(page-1)*page_size: page*page_size]:
            alerts = []
            errors = []
            for alert in event['alerts']:
                alerts.append({'media': alert['mediatypes'][0]['name'],
                               'error': alert['error']})
                errors.append(alert['error'])
            if all(errors):
                status = False
            elif any(errors):
                status = 'partial'
            else:
                status = True
            data.append(
                {
                    'clock': event['clock'],
                    'instance': event['hosts'][0]['host'],
                    'trigger': event['relatedObject']['description'],
                    'message': event['alerts'][0]['message'] if event['alerts'] else '',
                    'status': status,
                    'alerts': alerts
                }
            )

        return Response(
            {
                'count': len(event_list),
                'next': replace_query_param(url, 'pageNo', page+1) if len(event_list) > page*page_size else None,
                'previous': replace_query_param(url, 'pageNo', page-1) if (page-1) > 0 else None,
                'results': data
            }
        )


class WebsiteEventViewSet(viewsets.ViewSet):
    """
    站点告警事件视图
    """

    schema = ManualSchema(fields=[
        coreapi.Field(
            'pageNo',
            required=False,
            location='query',
            schema=coreschema.String(
                description='页码',
                pattern=r'\d+'
            )
        ),
        coreapi.Field(
            'pageSize',
            required=False,
            location='query',
            schema=coreschema.String(
                description='分页大小',
                pattern=r'\d+'
            )
        ),
        coreapi.Field(
            'websiteid',
            required=False,
            location='query',
            schema=coreschema.String(
                description="站点的ID, 如d3e1f285-95ea-4cf9-9738-807d3d9ee31e"
            )
        ),
        coreapi.Field(
            'from',
            required=False,
            location='query',
            schema=coreschema.String(
                description='Unix timestamp like 1587091000000',
                pattern=r'\d{13}'
            )
        ),
        coreapi.Field(
            'to',
            required=False,
            location="query",
            schema=coreschema.String(
                description='Unix timestamp like 1587091000000',
                pattern=r'\d{13}'
            )
        )
    ], description='查询站点告警事件')

    def list(self, request, *args, **kwargs):
        page = int(request.GET.get('pageNo', 1))
        page_size = int(request.GET.get('pageSize', 10))
        time_from = request.GET.get('from', None)
        time_till = request.GET.get('to', None)
        websiteid = request.GET.get('websiteid', None)
        url = request.build_absolute_uri()
        data = []
        params = {
            'tags': [{'tag': 'user', 'value': str(request.user.id)}],
            'selectHosts': 'extend',
            'select_alerts': 'extend',
            'selectRelatedObject': 'extend',
            'limit': 500
        }

        if time_from:
            params['time_from'] = time_from
        if time_till:
            params['time_till'] = time_till

        if websiteid:
            website = Website.objects.get(id=websiteid).value
            params['objectids'] = website.trigger_id
        else:
            websites = Website.objects.filter(owner=request.user)
            params['objectids'] = [v[0] for v in websites.values_list('trigger_id')]
        event_list = ZBXClient.event.get(**params)
        for event in event_list[(page-1)*page_size: page*page_size]:
            alerts = []
            errors = []
            if websites:
                website = websites.get(trigger_id=event['objectid'])
            for alert in event['alerts']:
                alerts.append({'media': alert['mediatypes'][0]['name'],
                               'error': alert['error']})
                errors.append(alert['error'])
            if all(errors):
                status = False
            elif any(errors):
                status = 'partial'
            else:
                status = True
            data.append(
                {
                    'clock': event['clock'],
                    'instance': website.name,
                    'trigger': event['relatedObject']['description'],
                    'message': event['alerts'][0]['message'] if event['alerts'] else '',
                    'status': status,
                    'alerts': alerts
                }
            )
        return Response(
            {
                'count': len(event_list),
                'next': replace_query_param(url, 'page', page+1) if len(event_list) > page*page_size else None,
                'previous': replace_query_param(url, 'page', page-1) if (page-1) > 0 else None,
                'results': data
            }
        )
