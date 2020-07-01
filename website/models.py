import uuid

from django.db import models
from django.utils import timezone

from portal.models import User


class Website(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('名称', blank=False, null=False, max_length=120,
                            db_index=True)
    url = models.CharField('URL', blank=False, null=False, max_length=120,
                           help_text='有效网址http(s)://xxx.xxx(/xxx)')
    enabled = models.BooleanField('是否启用', default=True)
    hc_item_id = models.IntegerField('HTTP状态码监控项ID', blank=True, null=True)
    lt_item_id = models.IntegerField('加载时间监控项ID', blank=True, null=True)
    kw_item_id = models.IntegerField('关键字匹配监控项ID', blank=True, null=True)
    trigger_id = models.IntegerField('触发器ID', blank=True, null=True)
    status_code = models.IntegerField('HTTP状态码', blank=True, null=True,
                                      help_text='1xx-5xx范围内的3位数字')
    keyword = models.CharField('匹配关键字', default='', max_length=120)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                              related_name='+')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True,
                                      verbose_name='创建时间')

    class Meta:
        ordering = ['created_at']
