from django.shortcuts import render
from django.db import models, router
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from django.db.models.functions import Trunc
from django.db.models import Count, Q
from rest_framework.schemas import ManualSchema, AutoSchema
from rest_framework.permissions import IsAuthenticated
from dashboard.models import UserSettings, Config
from dashboard.serializers import UserSettingsSerializer, HistorySerializer, ConfigSerializer
from rest_framework import mixins, generics, mixins, filters
from rest_framework.permissions import OR
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from dashboard.filters import ConfigFilter
from django_filters.rest_framework import DjangoFilterBackend
import json
import coreapi
import coreschema
from time import time
import requests
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import logging

from common.clients import ZBXClient
# Create your views here.
LOG = logging.getLogger('collie')


class Mypagination(PageNumberPagination):
    """
    表格默认排序，10条
    """
    # page_size_query_param = 'page_size'
    # page_query_param = 'page'
    # max_page_size = None
    page_size = 10
    page_size_query_param = 'pageSize'
    page_query_param = 'pageNo'


class MyAllpagination(PageNumberPagination):
    """
    获取所有信息的表格排序，默认不分页
    """
    page_size_query_param = 'pageSize'
    page_query_param = 'pageNo'


class UserSettingViewSet(viewsets.ModelViewSet):
    """
    允许用户查看或编辑的用户设置 API路径。
    """
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    ordering_fields = ('created_at',)
    pagination_class = MyAllpagination

    def get_queryset(self):
        config_obj = UserSettings.objects.filter(user=self.request.user)
        return config_obj

    @action(methods=['post'], detail=False, schema=AutoSchema(manual_fields=[
            coreapi.Field(
                'dingding',
                required=False,
                location='query',
                schema=coreschema.String(description='dingding webhook')
            )]))
    def testdingding(self, request, *args, **kwargs):
        """
        测试钉钉告警
        """
        try:
            dingding = request.data.get('dingding')
            webhook_url = dingding
            webhook_title = '测试钉钉告警'
            alert_message = '测试钉钉告警'
            webhook_header = {
                "Content-Type": "application/json",
                "charset": "utf-8"
            }
            webhook_message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": webhook_title,
                    "text": alert_message
                }
            }
            sendData = json.dumps(webhook_message, indent=1)
            result = requests.post(url=webhook_url, headers=webhook_header, data=sendData)
        except Exception as e:
            LOG.error(e)
            return Response(status=203, data=str(e))
        return Response(status=result.status_code, data=result.text)

    @action(methods=['post'], detail=False, schema=AutoSchema(manual_fields=[
            coreapi.Field(
                'email',
                required=False,
                location='query',
                schema=coreschema.String(description='email测试')
            )]))
    def testemail(self, request, *args, **kwargs):
        """
        测试邮件告警
        """
        SMTP = {
            'username': 'sentinel@huored.com',
            'password': '8issHFw4s',
            'hostname': 'smtp.huored.com',
            'is_ssl': True
        }

        try:
            send_email = request.data.get('email')
            email_title = '邮件告警测试'
            alert_message = '邮件告警测试'
            msg = MIMEText("""%s""" % (alert_message), "plain", "utf-8")
            msg['Subject'] = Header(email_title, 'utf-8').encode()
            msg['From'] = SMTP['username']
            msg['To'] = send_email
            smtp = SMTP_SSL(SMTP['hostname'])
            smtp.login(SMTP['username'], SMTP['password'])
            smtp.sendmail(SMTP['username'], send_email, msg.as_string())
            smtp.quit()
        except smtplib.SMTPException:
            return Response(status=203, data='无法发送邮件')
        return Response(status=200, data='success')


class HistoryViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    允许查看当前用户的历史数据 API路径
    """
    serializer_class = HistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    ordering_fields = ('created_at',)
    pagination_class = MyAllpagination

    def get_queryset(self):
        config_obj = Config.objects.filter(user=self.request.user)
        return config_obj

    @action(methods=['post'], detail=False, schema=AutoSchema(manual_fields=[
            coreapi.Field(
                'itemids',
                required=False,
                location='query',
                schema=coreschema.String(description='item数组')
            ),
            coreapi.Field(
                'time_from',
                required=False,
                location='query',
                schema=coreschema.String(description='开始时间戳, 默认为前60分钟的时间戳')
            ),
            coreapi.Field(
                'time_till',
                required=False,
                location='query',
                schema=coreschema.String(description='结束时间戳, 默认为当前时间戳')
            )
            ]))
    def loadtime(self, request, *args, **kwargs):
        """
        监控项历史数据，单位秒
        """
        time_from = request.data.get('time_from', int(time()//60*60) - 3600)
        time_till = request.data.get('time_till')
        itemids = json.loads(request.data.get('itemids'))
        params = {
            'itemids': itemids,
            'time_from': time_from,
            'history': 0,
            'output': ['clock', 'value', 'itemid']
        }
        if time_till:
            params['time_till'] = time_till
        history = ZBXClient.history.get(**params)
        data_generator = map(lambda x:
                             {
                                 'itemid': int(x['itemid']),
                                 'time': int(x['clock']),
                                 'value': float(x['value'])
                             },
                             history)
        data = [d for d in data_generator]
        return Response(data)


class ConfigViewSet(viewsets.ModelViewSet):
    """
    允许用户配置监控图表信息 API路径
    """
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    ordering_fields = ('created_at',)
    pagination_class = MyAllpagination

    def get_queryset(self):
        return Config.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """允许用户查询仪表盘信息"""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """允许用户保存仪表盘信息"""
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """允许用户更新仪表盘信息"""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """允许用户删除仪表盘信息"""
        return super().destroy(request, *args, **kwargs)
