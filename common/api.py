#!/usr/bin/env python
# set coding: utf-8
# @Time : 20-6-1 下午5:42
# @File : api.py
# @Author : richard zhu
# @purpose :

from .pagination import pages
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework import status
import logging
import time
logger = logging.getLogger('collie')

def exectime(func):
    def deco(*args, **kwargs):
        origin = time.time()
        callback = func(*args, **kwargs)
        now = time.time()
        logger.error(f"{func.__name__} 花费了{now - origin}秒时间")
        return callback
    return deco

def pagereturn(ret_obj, request):
    if isinstance(ret_obj, (list)):

        current_page = int(request.GET.get('pageNo', 0))
        page_size = int(request.GET.get('pageSize', 10))

        post_objects, pageObjects, totalPages, pageNo, pageSize, total = pages(ret_obj, page_size, current_page)

        if request.GET.get("count", "") == "1":
            ret = dict(
                pageObjects=None,
                totalPages=None,
                pageNo=None,
                pageSize=None,
                total=total
            )
        elif current_page:
            ret = dict(
                pageObjects= pageObjects,
                totalPages=totalPages,
                pageNo=pageNo,
                pageSize=pageSize,
                total=total
            )
        else:
            # 默认请求不分页返回所有+总数
            ret = dict(
                pageObjects=post_objects,
                totalPages=None,
                pageNo=None,
                pageSize=None,
                total=total
            )

        return JsonResponse(ret)
    else:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
