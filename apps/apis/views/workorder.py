#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
#from apps.usermanage.views.permission import PermissionVerify

from plugins.apps.workorder import dailywo_close, dailywo_reboot, dailywo_get_fault, dailywo_get_status, dailywo_putaway, daily_osinstall, daily_osinstall_update
from plugins.apps.workorder import repairwo_new, repairwo_update, repairwo_close, repairwo_get_status
#from django.utils import simplejson
import simplejson as json
import logging
logger = logging.getLogger('api')


#@login_required()
#@PermissionVerify()
@csrf_exempt
def dailywo(request):
    if request.method == "POST":
        received_json_data = json.loads(request.body)
        logger.info("参数(args):{0}".format(str(received_json_data)))
        for item in received_json_data:
            try:
                action = item["action"]
                logger.info("当前操作(action):{0}".format(action))
                if action == "close":
                    json_data = dailywo_close(item)
                elif action == "get_fault":
                    json_data = dailywo_get_fault(item)
                elif action == "get_status":
                    json_data = dailywo_get_status(item)
                elif action == "putaway":
                    json_data = dailywo_putaway(item)
                elif action == "reboot":
                    json_data = dailywo_reboot(item)
                elif action == "osinstall":
                    json_data = daily_osinstall(item)
                elif action == "osinstall_update":
                    json_data = daily_osinstall_update(item)
                else:
                    json_data = {
                        'code': 400,
                        'message': '没有获取到支持的操作类型!',
                        'ids': []
                    }
            except Exception, ex:
                print ex
                logger.error("Exception:%s" % (str(ex)))
                # 参数有误
                json_data = {
                    'code': 400,
                    'message': '提供的参数不完整或类型值不对!',
                    'ids': []
                }
    else:
        # 没有提供参数
        json_data = {'code': 400, 'message': '没有提供参数!', 'ids': []}
    logger.info("操作结果(result):" + str(json.dumps(json_data)))
    return HttpResponse(json.dumps(json_data, ensure_ascii=False))


#@login_required()
#@PermissionVerify()
@csrf_exempt
def repairwo(request):
    if request.method == "POST":
        received_json_data = json.loads(request.body)
        logger.info("参数(args):" + str(received_json_data))
        for item in received_json_data:
            try:
                action = item["action"]
                if action == "close":
                    json_data = repairwo_close(item)
                elif action == "new":
                    json_data = repairwo_new(item)
                elif action == "update":
                    json_data = repairwo_update(item)
                elif action == "get_status":
                    json_data = repairwo_get_status(item)
                else:
                    json_data = {
                        'code': 400,
                        'message': '没有获取到支持的操作类型!',
                        'ids': []
                    }
            except Exception, ex:
                print ex
                logger.error("Exception:%s" % (str(ex)))
                # 参数有误
                json_data = {'code': 400, 'message': '提供的参数不完整或类型值不对!'}
    else:
        # 没有提供参数
        json_data = {'code': 400, 'message': '没有参数!', 'ids': []}
    logger.info("操作结果(result):%s" % (str(json.dumps(json_data))))
    return HttpResponse(json.dumps(json_data, ensure_ascii=False))
