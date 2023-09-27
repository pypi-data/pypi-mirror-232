import json
import traceback
from datetime import datetime

import requests
from django.conf import settings
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import JsonResponse


def deal_request(request):
    """构建请求参数"""
    request_data = dict()
    # noinspection PyBroadException
    try:
        request_data.update(json.loads(request.body))
    except Exception:
        request_data.update(request.GET.dict())
        request_data.update(request.POST.dict())
    if settings.DEBUG:
        print("请求参数:", request_data)
    return request_data


def build_response(response):
    """构建返回数据"""
    if settings.DEBUG:
        print("返回参数：", response)
    return JsonResponse(status=200, data=response, json_dumps_params={"ensure_ascii": False},
                        content_type="application/json,charset=utf-8")


def build_error_response(code, msg):
    """构建失败的返回数据"""
    response = {'code': code, 'msg': msg, 'data': '',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    return build_response(response)


def build_success_response(response_data='', msg='', **kwargs):
    """构建请求成功地返回数据"""
    response = {'code': '1000', 'msg': msg, 'data': response_data,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    response.update(**kwargs)
    return build_response(response)


def paginator_util(obj_set, page_number=1, page_size=1000):
    """分页工具"""

    result = dict()
    paginator = Paginator(obj_set, page_size)
    try:
        page_list = paginator.page(page_number)
    except PageNotAnInteger:
        page_list = paginator.page(1)
    except EmptyPage:
        page_list = paginator.page(paginator.num_pages)
    result['count'] = paginator.count  # 总数量
    result['num_pages'] = paginator.num_pages  # 总页数
    result['page_size'] = paginator.per_page  # 每页数量
    result['page_number'] = page_number  # 当前页码
    return result, page_list.object_list


def tuple_to_list(params):
    """将映射关系元组转换成列表"""
    res = []
    for i in params:
        res.append({"value": i[0], "label": i[1]})
    return res


def str_to_date(params):
    """字符串转date类型"""
    return datetime.strptime(params, "%Y-%m-%d").date()


def str_to_datetime(params):
    """字符串转datetime类型"""
    return datetime.strptime(params, "%Y-%m-%d %H:%M:%S")


def date_to_str(params):
    """date类型转字符串"""
    return params.strftime("%Y-%m-%d")


def datetime_to_str(params):
    """datetime类型转字符串"""
    return params.strftime("%Y-%m-%d %H:%M:%S")


def do_request(url, req_data, method="POST"):
    """发送请求"""
    # noinspection PyBroadException
    try:
        if method == "POST":
            response = requests.post(url, json=req_data, timeout=10)
        else:
            response = requests.get(url, params=req_data, timeout=10)
    except Exception:
        return False, 0, f"请求异常：{traceback.format_exc()}"
    else:
        if response.status_code != 200:
            return True, response.status_code, response.text
        return True, response.status_code, response.json()
