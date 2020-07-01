from django.db import models
from portal.models import User
import uuid
# Create your models here.


class UserSettings(models.Model):
    """用户配置"""
    name = models.CharField(max_length=50, verbose_name=u'用户名称', help_text='用户名称')
    email = models.CharField(max_length=50, verbose_name=u'email地址', help_text='email地址')
    phone = models.CharField(max_length=50, verbose_name=u'联系方式', help_text='联系方式')
    dingding = models.CharField(max_length=250, verbose_name=u'钉钉机器人token', help_text='钉钉机器人token')
    proxy_uuid = models.UUIDField(verbose_name='proxy 注册ID', default=uuid.uuid4, editable=False,)
    proxy = models.CharField(max_length=250, verbose_name=u'zabbix proxy安装脚本', help_text='zabbix proxy安装脚本')
    linux_agent = models.CharField(max_length=250, verbose_name=u'linux agent安装脚本', help_text='linux agent安装脚本')
    windows_agent = models.CharField(max_length=250, verbose_name=u'windows agent安装脚本', help_text='windows agent安装脚本')
    is_alarm = models.CharField(max_length=1, verbose_name=u'是否告警', help_text='是否告警')
    media_types = models.TextField(verbose_name=u'告警媒介', help_text='告警媒介')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True,
                                      verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True,
                                      verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['user']
        verbose_name = u'用户配置'


class Config(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    config = models.TextField(verbose_name=u'配置信息')
    created_at = models.DateTimeField(auto_now_add=True,
                                      null=True,
                                      verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True,
                                      null=True,
                                      verbose_name="更新时间")

    class Meta:
        unique_together = ['user']
        ordering = ['created_at']

