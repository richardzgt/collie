import logging
import traceback

from django.conf import settings
from rest_framework import serializers
from common.clients import ZBXClient
from dashboard.models import UserSettings, Config

LOG = logging.getLogger('collie')


class UserSettingsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(allow_blank=True, required=False)
    email = serializers.CharField(allow_blank=True, required=False)
    phone = serializers.CharField(allow_blank=True, required=False)
    dingding = serializers.CharField(allow_blank=True, required=False)
    proxy = serializers.CharField(allow_blank=True, required=False)
    linux_agent = serializers.CharField(allow_blank=True, required=False)
    windows_agent = serializers.CharField(allow_blank=True, required=False)
    is_alarm = serializers.CharField(allow_blank=True, required=False)
    media_types = serializers.JSONField(required=False)

    class Meta:
        model = UserSettings
        fields = ['id', 'name', 'email', 'phone', 'dingding', 'proxy', 'linux_agent', 'windows_agent',
                  'is_alarm', 'media_types']

    def create(self, validated_data):
        validated_data['user'] = self._context['request']._user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['user'] = self._context['request']._user
        return super().update(instance, validated_data)


class ConfigSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    config = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = Config
        fields = ['id', 'config']

    def create(self, validated_data):
        validated_data['user'] = self._context['request']._user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['user'] = self._context['request']._user
        return super().update(instance, validated_data)


class HistorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    config = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    user = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Config
        fields = ['id', 'user', 'config']
    #
    # def create(self, validated_data):
    #     validated_data['user'] = self._context['request']._user
    #     validated_data['result'] = self.get_history()
    #     return super().create(validated_data)
    #
    # def update(self, instance, validated_data):
    #     validated_data['user'] = self._context['request']._user
    #     validated_data['result'] = self.get_history()
    #     return super().update(instance, validated_data)
    #
    # def get_history(self):
    #     try:
    #         response = ZBXClient.history.get(
    #             {
    #                 'history': self.history,
    #                 'itemids': self.itemids,
    #                 'hostids': self.hostids,
    #                 'time_from': self.time_from,
    #                 'time_till': self.time_till
    #             }
    #         )
    #     except Exception as e:
    #         LOG.error(f"failed to get history" + traceback.format_exc())
    #         raise e
    #     return response
