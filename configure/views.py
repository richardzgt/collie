import logging
import traceback
import time
from math import ceil
from portal.models import User
from common.clients import ZBXClient as API
from common.api import pagereturn, exectime
from .MySchema import (TriggerViewSchema,
                       HostViewSchema,
                       ItemViewSchema,
                       ApplicationViewSchema)
from dashboard.models import UserSettings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http.response import HttpResponseBadRequest

# Create your views here.
logger = logging.getLogger('collie')

class MyException(object):
    pass

def get_triggers(**kwargs):
    triggers = API.trigger.get(**kwargs,
                              expandExpression=True,
                              output=["expression", "description", "value", "state", "status", "error"],
                              selectItems="extend",
                              selectTags="extend",
                              selectHosts="extend")
    return triggers

def get_hosts(**kwargs):
    if kwargs.get('noPage'):
        return API.host.get(**kwargs, output=['hostid', 'host'])

    hosts = API.host.get(**kwargs,
                         selectParentTemplates=['templateid', 'name'],
                         output=['hostid', 'proxy_hostid', 'error', 'host', 'available', 'status',
                                'snmp_available', 'snmp_error'])
    return hosts


def get_items(**kwargs):
    items = API.item.get(**kwargs,
                         output="extend",
                         selectApplications="extend",
                         selectHosts="extend",
                         selectTriggers="extend")
    return items


class HostViewSet(ViewSet):
    """
    主机视图
    """
    permission_classes = [IsAuthenticated]
    # authentication_classes = []
    schema = HostViewSchema()

    def create(self, request):
        """
        :param request:
        host: test01
        insterfaces: [{"type":"1", "main":"1", "useip":"1", "ip":"10.0.99.1", "dns":"" ,"port":"10050"}]
        templates: ["10267", "10001"]
        :return:
        """
        host = request.data.get("host")   # 主机名 zabbix agent要匹配客户端配置，如果是snmp则是ip地址
        user = User.objects.get(id=request.user.id)
        interfaces = request.data.get("interfaces") # 按照zabbix的interfaces格式
        templates = request.data.get("templates")

        try:
            this_host = API.host.get(filter={"host": [host]}, output=["host"])
            assert  this_host == [], "已创建host"
            ret_host = API.host.create(
                host=host,
                interfaces=interfaces,
                groups=[dict(groupid=user.zbx_gid)],
                templates=templates  # [10267,10001] 模板id
            )

            hostid = ret_host['hostids']
            setting = UserSettings.objects.get(user=user)
            proxy_hosts = API.proxy.get(proxyids=setting.proxy_uuid, selectHosts="extend")

            for host in proxy_hosts[0]['hosts']:
                hostid.append(host['hostid'])

            ret_proxy = API.proxy.update(proxyid=setting.proxy_uuid, hosts=hostid)

        except AssertionError as e:
            return Response(status=status.HTTP_409_CONFLICT, data=str(e))

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_201_CREATED)

    # @exectime
    def list(self, request):
        """
        :param request:
        :param filter_key:
        :param filter_value:
        :return:
        """
        try:
            user = User.objects.get(id=request.user.id)
            hostid = request.GET.get("hostid", "")
            search_host = request.GET.get("host", "")
            available = request.GET.get("available", "") # 默认选择所有主机
            status = request.GET.get("status", "")

            filter = dict()
            search = dict()
            if hostid:
                filter.update(dict(hostid=hostid))

            if status:
                filter.update(dict(status=status))

            if search_host:
                search['host'] = search_host

            hosts = get_hosts(groupids=user.zbx_gid, filter=filter, search=search)
            host_ret = []

            def _slice(str):
                if len(str)>30:
                    _str = str[0:50] + '.....'
                else:
                    _str = str
                return _str

            for host in hosts:
                if available == "1":
                    if not any((int(host['available']) ,int(host['snmp_available']))):
                        continue

                ret = API.hostinterface.get(hostids=host['hostid'])
                host_ret.append({
                    'host': host['host'],
                    'hostid': int(host['hostid']),
                    'error': host['error'] if host['error'] else host['snmp_error'],
                    'available': int(host['available']) if int(host['available']) else int(host['snmp_available']),
                    'status': int(host['status']),
                    'templates': [ _slice(each['name']) for each in host['parentTemplates'] ],
                    'interfaceid': ret[0]['interfaceid'],
                    'interface_type': int(ret[0]['type']),
                    'interface_ip': ret[0]['ip'],
                    'interface_port': ret[0]['port']
                })

            return pagereturn(host_ret, request)

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        try:

            host = get_hosts(hostids=[pk])[0]
            ret = API.hostinterface.get(hostids=host['hostid'])
            host.update(dict(interface=ret[0]))

        except IndexError as e:
            return  Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(host)

    def update(self, request, pk):
        """
        修改host
        :param request:
        :param id:
        interfaces:
        host:
        status:
        templates:
        :return:
        """
        interfaces = request.data.get('interfaces', '')
        host = request.data.get('host', '')
        status = request.data.get('status', '')
        templates = request.data.get('templates', '')

        update_kwargs = {}

        if interfaces:
            update_kwargs.update(dict(interfaces=interfaces))
        if status in (0, 1):
            update_kwargs.update(dict(status=status))
        if host:
            update_kwargs.update(dict(host=host))
        if templates:  # [10267,10001] 模板id
            update_kwargs.update(dict(templates=templates))

        print(update_kwargs)
        try:
            ret = API.host.update(
                                hostid=pk,
                                **update_kwargs
            )

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(ret)

    def destroy(self, request, pk):
        user = User.objects.get(id=request.user.id)
        host = get_hosts(hostids=pk, groupids=user.zbx_gid)
        if host:
            ret = API.host.delete(pk)
            return Response(ret)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class TemplateViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        默认模板组，用于默认监控项的模板关联
        如果需要用户自定义监控项，则zabbix后台手工添加关联主机组和模板
        :param request:
        :return:
        """
        try:
            # user = User.objects.get(id=request.user.id)
            groupids = API.hostgroup.get(filter={"name": ["custom-normal-Templates"]}, output=['groupid']) # 获取模板组的id
            groupid = groupids[0]['groupid']
            if groupid:
                ret = API.template.get(output=['name','description','templateids'], groupids=groupid)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(ret)

class ApplicationViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    schema = ApplicationViewSchema()
    def list(self, request):
        """
        通过hostid 获取应用集
        :param request:
        :return:
        """
        try:
            hostid = request.GET.get("hostid", "")
            assert hostid, "必须输入hostid"
            applications = API.application.get(hostids=hostid, output=['applicationid', 'name'])
            return Response(applications)
        except AssertionError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        except Exception as e:
            logger.error(traceback.format_exc())
            return  Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TriggerViewSet(ViewSet):
    """
    触发器视图，不提供删除触发器
    """
    permission_classes = [IsAuthenticated]
    schema = TriggerViewSchema()
    _suffix = "custom"

    def list(self, request):
        """
        :param request:
        :return:
        主机
        触发器描述    description
        触发器表达式  expression
        触发器状态　   value
        触发器是否启动　status
        获取触发器状态    state
        触发器错误状态原因   error
        主机信息        host
        监控项信息      item
        """

        hostid = request.GET.get("hostid", "")
        state = request.GET.get("state", "")
        status = request.GET.get("status", "")
        value = request.GET.get("value", "")
        user = User.objects.get(id=request.user.id)

        filter=dict()
        if hostid:
            filter.update(dict(hostid=hostid))
        if state:
            filter.update(dict(state=state))
        if status:
            filter.update(dict(status=status))
        if value:
            filter.update(dict(value=value))

        triggers = get_triggers(groupids=user.zbx_gid, filter=filter)

        trigger_ret = []
        for trigger in triggers:
            if len(trigger['tags']) > 0: # 判断是否有discard标签
                if trigger['tags'][0].get("value") == 'true' and \
                   trigger['tags'][0].get('tag') == 'discard':
                   continue
            if trigger['description'].find(self._suffix) > 0: # 判断是否有后缀标签
                trigger['description'] = trigger['description'].split("|")[0]
            trigger_ret.append(
                {
                    'triggerid': trigger['triggerid'],
                    'description': trigger['description'],
                    'expression': trigger['expression'],
                    'value': trigger['value'],
                    'status': trigger['status'],
                    'state': trigger['state'],
                    'error': trigger['error'],
                    'host': trigger['hosts'][0]['host'],
                    'item': trigger['items'][0]['name']
                }
            )

        return pagereturn(trigger_ret, request)

    def retrieve(self, request, pk):
        """
        获取单个触发器
        :param request:
        :param pk:
        :return:
        """
        trigger = get_triggers(triggerids=pk)
        if len(trigger) >0 :
            desc = trigger[0]['description']
            if desc.find(self._suffix) > 0:
                trigger[0]['description'] = desc.split("|")[0]
        return  Response(trigger)

    def update(self, request, pk):
        """
        只提供表达式和触发器状态的更新
        :param request:
        :param pk:
        :param expression
        :param  trigger_status
        :return:
        """
        trigger = API.trigger.get(triggerids=pk,
                                  output=["description", "expression", "priority", "templateid"],
                                  selectTags="extend",
                                  selectDependencies="triggerid",
                                  expandExpression=True)
        expression = request.data.get("expression", "")
        trigger_status = request.data.get("status", "0")
        try:
            assert len(trigger) == 1, "can not found trigger"
            trigger_obj = trigger[0]
            origin_trigger_id = trigger_obj.pop("triggerid")
            # print(trigger_obj)
            if trigger_obj['templateid'] != "0":
                # 如果是模板继承，则无法修改,先创建一个自定义的触发器，再把原来触发器关闭
                trigger_obj.pop('templateid')
                trigger_obj['description'] = f"{trigger_obj['description']}|{self._suffix}"
                trigger_obj['expression'] = expression # 只支持改触发规则
                trigger_obj['status'] = trigger_status
                new_trigger_id = API.trigger.create(trigger_obj)
                ret = API.trigger.update(triggerid=origin_trigger_id,
                                   status=1,
                                   tags=[{"tag":"discard", "value":"true", "operator":"1"}])
            else:
                ret = API.trigger.update(triggerid=origin_trigger_id,
                                   status=trigger_status,
                                   expression=expression)

        except AssertionError as e:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return  Response(ret)

class ItemViewSet(ViewSet):
    """
    监控项视图
    """
    permission_classes = [IsAuthenticated]
    schema = ItemViewSchema()

    def list(self, request):
        """
        :param request:
        :return:
            名称    ['name']
            触发器  ['triggers'][*]['description']
            间隔    ['delay']
            实例    ['hosts'][0]['host']
            应用集名称  ['applications'][0]['name']
            状态      ['state']  0 可用
            启用状态(操作)  ['status'] 0 已启用
        """

        hostid = request.GET.get("hostid", "")
        applicationids = request.GET.get("applicationids", "")
        value_type = request.GET.getlist("value_type", "")

        user = User.objects.get(id=request.user.id)
        filter = dict()
        query = dict()
        if hostid :
            filter.update(dict(hostid=hostid))

        if applicationids:
            query.update(dict(applicationids=applicationids))

        if value_type:
            filter.update(dict(value_type=value_type))

        items = get_items(groupids=user.zbx_gid,
                          filter=filter, **query)

        items_ret = []
        for item in items:
            items_ret.append(
                {
                    'name': item['name'],
                    'itemid': item['itemid'],
                    'triggers': item['triggers'],
                    'delay': item['delay'],
                    'host': item['hosts'][0]['host'],
                    'hostid': item['hosts'][0]['hostid'],
                    'state': item['state'], # 触发器状态
                    'status': item['status'], # 启用状态
                    'applications': item['applications'][0]['name'] if item['applications'] else None
                }
            )

        return pagereturn(items_ret, request)

    def retrieve(self, request, pk):
        user = User.objects.get(id=request.user.id)
        item = get_items(itemids=pk)
        if item:
            return Response(item)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        """
        监控项更新
        只更新item的状态
        :param request:
        status
        :param pk:
        :return:
        """
        user = User.objects.get(id=request.user.id)
        status = request.data.get("status", 0)
        try:
            item = get_items(itemids=pk, groupids=user.zbx_gid)
            assert  item, "找不到这个监控项"
            ret = API.item.update(itemid=pk, status=status)

        except AssertionError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(ret)


    @action(methods=['get'], detail=True)
    def test(self, request, pk):
        """
        监控项测试方法
        :param request:
        :param pk:
        :return:
        """
        try:
            item = API.item.get(output=["value_type"], itemids=pk)
            ret = API.task.create(type=6, itemids=pk)
            if not ret:
                raise Exception(f"监控项{pk}测试失败了")
            time_from_timestamp = ceil(time.time())
            cnt = 30
            history_ret = []
            while cnt > 0:
                history_ret = API.history.get(itemids=pk,
                                              time_from=time_from_timestamp,
                                              history=item[0]['value_type'] # 指定item类型 0 float ；3 numeric unsigned
                                              )
                logger.debug(f"测试监控项{pk}消耗了{cnt}秒")
                if history_ret:
                    break
                time.sleep(1)
                cnt -= 1
            history_ret[0]['elasped']=int(history_ret[0]['clock'])-time_from_timestamp
        except IndexError:
            return Response(status=status.HTTP_504_GATEWAY_TIMEOUT, data=u"execute timeout")
        except Exception as e:
            logger.error(traceback.format_exc())
            return  Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(history_ret)

