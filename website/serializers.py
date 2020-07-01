import logging
import traceback

from django.conf import settings
from rest_framework import serializers

from common.clients import ZBXClient
from website.models import Website


LOG = logging.getLogger('collie')


class WebsiteSerializer(serializers.ModelSerializer):
    status_code = serializers.IntegerField(max_value=599, min_value=100,
                                           required=False)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S',
                                           read_only=True)
    keyword = serializers.CharField(default='')

    class Meta:
        model = Website
        fields = ['id', 'name', 'url', 'status_code',
                  'keyword', 'enabled', 'created_at']

    def validate(self, attrs):
        if attrs.get('status_code') or attrs.get('keyword'):
            return attrs
        detail = {'status_code': self.error_messages['required']}
        raise serializers.ValidationError(detail, code='required')

    def create(self, validated_data):
        name = validated_data['name']
        url = validated_data['url']
        keyword = validated_data['keyword']
        status_code = validated_data.get('status_code', '')
        validated_data['owner'] = self._context['request']._user
        try:
            items_response = ZBXClient.item.create(
                {
                    'name': f"{self._context['request']._user.id} {name}状态码",
                    'key_': f'web.page.get[{url},,]',
                    'hostid': settings.ZABBIX_WEB_MONITOR_HOSTID,
                    'interfaceid': settings.ZABBIX_WEB_MONITOR_INTERFACEID,
                    'type': 0,
                    'value_type': 1,
                    'delay': '3m',
                    'preprocessing': [
                        {
                            'type': 5,
                            'params': '.*?(\d{3}).*\n\\1',
                            'error_handler': 0,
                            'error_handler_params': ''
                        }
                    ]
                },
                {
                    'name': f"{self._context['request']._user.id} {name}加载时间",
                    'key_': f'web.page.perf[{url},,]',
                    'hostid': settings.ZABBIX_WEB_MONITOR_HOSTID,
                    'interfaceid': settings.ZABBIX_WEB_MONITOR_INTERFACEID,
                    'type': 0,
                    'value_type': 0,
                    'delay': '3m',
                    'units': 's'
                },
                {
                    'name': f"{self._context['request']._user.id} {name}内容匹配关键字",
                    'key_': f'web.page.regexp[{url},,,{keyword},,]',
                    'hostid': settings.ZABBIX_WEB_MONITOR_HOSTID,
                    'interfaceid': settings.ZABBIX_WEB_MONITOR_INTERFACEID,
                    'type': 0,
                    'value_type': 4,
                    'delay': '3m'
                }
            )

            if status_code and keyword:
                expression = f"{{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].last(#1)}}<>\"{status_code}\" \
                or \
                {{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.regexp[{url},,,{keyword},,].strlen(#1)}}=0 \
                or \
                {{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].nodata(1m)}}=1"
            elif status_code:
                expression = f"{{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].last(#1)}}<>\"{status_code}\" \
                or \
                {{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].nodata(1m)}}=1"
            elif keyword:
                expression = f"{{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.regexp[{url},,,{keyword},,].strlen(#1)}}=0 \
                or \
                {{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].nodata(1m)}}=1"
            else:
                expression = f"{{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].nodata(1m)}}=1"
            trigger_response = ZBXClient.trigger.create(
                description=f'{name}状态码或关键字匹配失败',
                expression=expression,
                priority=5,
                tags=[
                    {
                        'tag': 'user',
                        'value': str(self._context['request']._user.id)
                    }
                ]
            )
        except Exception as e:
            LOG.error(f"failed to create website for user {self._context['request']._user.id} :" + traceback.format_exc())
            raise e
        validated_data['hc_item_id'] = items_response['itemids'][0]
        validated_data['lt_item_id'] = items_response['itemids'][1]
        validated_data['kw_item_id'] = items_response['itemids'][2]
        validated_data['trigger_id'] = trigger_response['triggerids'][0]
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.name)
        url = validated_data.get('url', instance.url)
        keyword = validated_data.get('keyword', instance.keyword)
        status_code = validated_data.get('status_code', instance.status_code)

        try:
            ZBXClient.item.update(
                {
                    'name': f"{self._context['request']._user.id} {name}状态码",
                    'key_': f'web.page.get[{url},,]',
                    'status': 1 if not instance.enabled else 0,
                    'itemid': instance.hc_item_id
                },
                {
                    'name': f"{self._context['request']._user.id} {name}加载时间",
                    'key_': f'web.page.perf[{url},,]',
                    'status': 1 if not instance.enabled else 0,
                    'itemid': instance.lt_item_id
                },
                {
                    'name': f"{self._context['request']._user.id} {name}内容匹配关键字",
                    'key_': f'web.page.regexp[{url},,,{keyword},,]',
                    'status': 1 if not instance.enabled else 0,
                    'itemid': instance.kw_item_id
                }
            )

            if status_code and keyword:
                expression = f"{{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].last(#1)}}<>\"{status_code}\" \
                or \
                {{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.regexp[{url},,,{keyword},,].strlen(#1)}}=0 \
                or \
                {{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].nodata(1m)}}=1"
            elif status_code:
                expression = f"{{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].last(#1)}}<>\"{status_code}\" \
                or \
                {{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].nodata(1m)}}=1"
            elif keyword:
                expression = f"{{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.regexp[{url},,,{keyword},,].strlen(#1)}}=0 \
                or \
                {{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].nodata(1m)}}=1"
            else:
                expression = f"{{{settings.ZABBIX_WEB_MONITOR_HOST}:web.page.get[{url},,].nodata(1m)}}=1"
            ZBXClient.trigger.update(
                description=f'{name}状态码或关键字匹配失败',
                expression=expression,
                triggerid=instance.trigger_id,
                status=1 if not instance.enabled else 0
            )
        except Exception as e:
            LOG.error(f"failed to update website for user {self._context['request']._user.id} :" + traceback.format_exc())
            raise e
        return super().update(instance, validated_data)
