#!/usr/bin/env python
# set coding: utf-8
# @Time : 20-6-9 上午11:17
# @File : MySchema.py
# @Author : richard zhu
# @purpose :

import coreapi
import coreschema
from rest_framework.schemas import ManualSchema, AutoSchema

class HostViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []

        if self._view.action == 'create':
            extra_fields = [
                coreapi.Field(
                    "host",
                    required=True,
                    location="form",
                    schema=coreschema.String(
                        description='提交主机名，like: yum.ops.net'
                    )
                ),
                coreapi.Field(
                    "interface",
                    required=True,
                    location="form",
                    schema=coreschema.String(
                        description='主机接口，like: [{"type":"1", "main":"1", "useip":"1", "ip":"10.0.99.1", "dns":"" ,"port":"10050"}] ',
                    )
                ),
                coreapi.Field(
                    "templates",
                    required=True,
                    location="form",
                    schema=coreschema.String(
                        description='模板列表，like: ["10267", "10001"]',
                    )
                ),
            ]

        elif self._view.action == 'update':
            extra_fields = [
                coreapi.Field(
                    "host",
                    required=False,
                    location="form",
                    schema=coreschema.String(
                        description='提交主机名，like: yum.ops.net',
                    )
                ),
                coreapi.Field(
                    "interfaces",
                    required=False,
                    location="form",
                    schema=coreschema.Array(
                        description='主机接口，like: [{"type":"1", "main":"1", "useip":"1", "ip":"10.0.33.1", "dns":"" ,"port":"10050"}]',
                    )
                ),
                coreapi.Field(
                    "status",
                    required=False,
                    location="form",
                    schema=coreschema.String(
                        description='主机监控状态，like: 0 启用， 1 停用',
                    )
                ),
            ]

        elif self._view.action == 'list':
            extra_fields = [
                coreapi.Field(
                    "hostid",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据主机id查询,like: 10330',
                    )
                ),
                coreapi.Field(
                    "host",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据主机名模糊查询,like: yum',
                    )
                ),
                coreapi.Field(
                    "available",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据可用性查询主机[1 可用，0不可用],'
                                    'like: available=1',
                    )
                ),
                coreapi.Field(
                    "status",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据启用状态查询主机[0 已启用，1 未启用],'
                                    'like: status=1',
                    )
                ),
                coreapi.Field(
                    "pageSize",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='分页列表数量，like: 10',
                    )
                ),
                coreapi.Field(
                    "pageNo",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='页序，like: 1',
                    )
                ),
                coreapi.Field(
                    "noPage",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='不分页，like: 1',
                    )
                ),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class TriggerViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if self._view.action == 'update':
            extra_fields = [
                coreapi.Field(
                    "expression",
                    required=False,
                    location="form",
                    schema=coreschema.String(
                        description='匹配表达式，like: {10.0.0.218}>{$CLICKHOUSE.DELAYED.FILES.DISTRIBUTED.COUNT.MAX.WARN}',
                    )
                ),
                coreapi.Field(
                    "trigger_status",
                    required=False,
                    location="form",
                    schema=coreschema.String(
                        description='设置触发器状态，like: 1 #启用 0 #关闭 ',
                    )
                ),
            ]

        elif self._view.action == 'list':
                # /api/configure/hostCreate
            extra_fields = [
                coreapi.Field(
                    "hostid",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据hostid过滤触发器，like: 10330',
                    )
                ),
                coreapi.Field(
                    "state",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据状态过滤触发器[0 正常，1 未知, 默认不过滤]，like: state=0',
                    )
                ),
                coreapi.Field(
                    "status",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据启用状态过滤触发器[0 启用， 1 停用, 默认不过滤]，like: status=0',
                    )
                ),
                coreapi.Field(
                    "value",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据状态过滤触发器[0 正常， 1 问题, 默认不过滤]，like: status=0',
                    )
                ),
                coreapi.Field(
                    "pageSize",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='分页列表数量，like: 10',
                    )
                ),
                coreapi.Field(
                    "pageNo",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='页序，like: 1',
                    )
                ),
                coreapi.Field(
                    "noPage",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='不分页[0|1]，like: 1',
                    )
                ),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields

# 自定义额外的参数
class ItemViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []

        if self._view.action == 'list':
            extra_fields = [
                coreapi.Field(
                    "hostid",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据主机id过滤，'
                                    'like: 10330',
                    )
                ),
                coreapi.Field(
                    "applicationids",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='根据应用集过滤监控项，like: 1348',
                    )
                ),
                coreapi.Field(
                    "value_type",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='过滤监控项的数据类型，like: 0 float , 1 character.....',
                    )
                ),

                coreapi.Field(
                    "pageSize",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='分页列表数量，like: 10',
                    )
                ),
                coreapi.Field(
                    "pageNo",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='页序，like: 1',
                    )
                ),
                coreapi.Field(
                    "noPage",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='不分页，like: 1',
                    )
                ),
            ]
        elif self._view.action == 'update':
            extra_fields = [
                coreapi.Field(
                    "status",
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description='设置监控项的启停，like: # 0 启动 1 关闭',
                    )
                ),
            ]

        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields

class ApplicationViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []

        if self._view.action == 'list':
            extra_fields = [
                coreapi.Field(
                    "hostid",
                    required=True,
                    location="query",
                    schema=coreschema.String(
                        description='提交主机id，like: 10330'
                    )
                ),
                ]

        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields
