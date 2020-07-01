from rest_framework.pagination import PageNumberPagination
from math import ceil
import logging

logger = logging.getLogger('collie')

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    page_query_param = 'pageNo'


def pages(post_objects, page_size, current_page=1):
    """
    :param post_objects: 数据对象
    :param current_page:  当前页面
    :param items_num:  每页
    :return:
    """
    try:

        total = len(post_objects)
    except ValueError:
        current_page = 1

    if page_size:
        total_pags = ceil(total/page_size)
    else:
        total_pags = None

    try:
        page_objects = post_objects[page_size*(current_page-1):page_size*current_page]
    except IndexError as e:
        logger.error(e)

           # 所有对象， 本页对象， 所有页码， 本页页码, 一页展示多少项, 总数
    return post_objects, page_objects, total_pags, current_page, page_size, total



