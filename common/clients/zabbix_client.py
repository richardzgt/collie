import logging
import requests

from pyzabbix import ZabbixAPI

from django.conf import settings


class ZBXClient(ZabbixAPI):

    def __init__(self, server=settings.ZABBIX_URL,
                 session=None, use_authenticate=False, timeout=None):
        super().__init__(server=settings.ZABBIX_URL,
                         session=None, use_authenticate=False, timeout=None)
        self.login(settings.ZABBIX_USER, settings.ZABBIX_PASSWORD)

API = ZBXClient()
