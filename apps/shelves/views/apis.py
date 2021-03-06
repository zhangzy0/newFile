#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response,RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.contrib.auth import authenticate 
from apps.usermanage.views.permission import PermissionVerify
from apps.workorder.models import FaultList, SpareBrandList
from apps.shelves.models import CheckCount, StandardData, CheckFailData, PowerOnTime
from plugins.myclass.shelves_models import StandardDataOb, CheckFailDataOb
from plugins.codegit.url_oper import post_urlopen
from datetime import date
import requests
import sys
import json
import re
import time
import datetime
import logging
import yaml
from apps.shelves.models import MachineFaults


reload(sys)
sys.setdefaultencoding('utf8')
logger = logging.getLogger('shelves')

@login_required
@PermissionVerify()
def getFaults(request):
    try:
        sn = request.GET.get("sn")
        print sn
        ob_std = StandardData.objects.get(std_sn = sn)
        entity_id = ob_std.std_entity_id
        faults = MachineFaults.objects.filter(fault_sn = sn)
    except Exception,ex:
        ob_std = ""
        faults = ""
    kwvars = {
        "faults": faults,
        "sn": sn,
        "item": ob_std,
    }
    return render_to_response('shelves/apigetfaults.html',kwvars)

@csrf_exempt
@login_required
@PermissionVerify()
def addFaults(requests):
    id_faults = requests.POST.getlist("id_fault")
    fault_models = requests.POST.getlist("fault_model")
    fault_locations = requests.POST.getlist("fault_location")
    fault_nums = requests.POST.getlist("fault_num")
    fault_descs = requests.POST.getlist("fault_desc")
    fault_sn = requests.POST["sn"]
    fault_entity_id = requests.POST["entity_id"]
    msg = ""
    ENV_FILE =  '/etc/maintain/website_env.yaml'
    try:
        with open( ENV_FILE ) as fp :
            ENV = yaml.load(fp)['env']
    except Exception,ex:
        ENV = "test"
    if fault_entity_id != "None":
        if ENV == "online":
            roc_url = "http://roc.sogou/pandora/report_fault/addManualIdx"
        else:
            roc_url = "http://test.roc.sogou/pandora/report_fault/addManualIdx"
        for i in range(len(id_faults)):
            try:
                id_fault = FaultList.objects.get(id_fault = int(id_faults[i]))
                values = {}
                values["entity_id"] = fault_entity_id
                values["sn"] = fault_sn
                values["id"] = "sat_error"
                values["plugin_name"] = "sat_error"
                values["idx"] = "sat_error"
                values["color"] = "red"
                values["num"] = fault_nums[i]
                values["desc"] = fault_descs[i]
                values["model"] = fault_models[i]
                values["location"] = fault_locations[i]
                values["value"] = id_fault.fault_cn
                values["type"] = id_fault.fault_en
                values = json.dumps(values)
                values = json.loads(values)
                ret_code,ret_info = post_urlopen(url = roc_url, values=values) 
                print values
                print roc_url
                print ret_code,ret_info
                # 200 {"val":190044,"ret":true}
                if ret_code == 200:
                    ret_info = json.loads(ret_info)
                    if ret_info["ret"] == True:
                        response_data = {"ret_code":200,"ret_info":"报障成功！","sn":fault_sn}
                        try:
                            ob_machine_fault = MachineFaults(id_fault = id_fault, fault_model = fault_models[i], 
                                                       fault_location = fault_locations[i], fault_sn = fault_sn,
                                                       fault_num = fault_nums[i], fault_desc = fault_descs[i])
                            ob_machine_fault.save()
                        except Exception,ex:
                            response_data = {"ret_code":400,"ret_info":"报障成功！","sn":fault_sn}
                    else:
                        response_data = {"ret_code":500,"ret_info":"{ret_err}，报障失败！".format(ret_err = ret_info["err"]),"sn":fault_sn}
                else:
                    response_data = {"ret_code":500,"ret_info":"接口故障，报障失败！","sn":fault_sn}
            except Exception,ex:
                print ex
                response_data = {"ret_code":500,"ret_info":"报障失败！","sn":fault_sn}
    else:
        response_data = {}
        if ENV == "online":
            roc_url = "http://roc.sogou/pandora/report_fault/run"
        else:
            roc_url = "http://test.roc.sogou/pandora/report_fault/run"
        values = {}
        values["sn"] = fault_sn
        values["user_id"] = "nieyingge"
        values["source"] = "rf_api"
        values["data"] = []
        for i in range(len(id_faults)):
            try:
                id_fault = FaultList.objects.get(id_fault = int(id_faults[i]))
                t_data = {}
                t_data["id"] = "sat_error"
                t_data["plugin_name"] = "sat_error"
                t_data["idx"] = "sat_error"
                t_data["color"] = "red"
                t_data["num"] = fault_nums[i]
                t_data["desc"] = fault_descs[i]
                t_data["model"] = fault_models[i]
                t_data["location"] = fault_locations[i]
                t_data["value"] = id_fault.fault_cn
                t_data["type"] = id_fault.fault_en
                values["data"].append(t_data)
            except Exception,ex:
                response_data = {"ret_code":500,"ret_info":"报障失败！","sn":fault_sn}
        values["data"] = json.dumps(values["data"])
        values = json.dumps(values)
        values = json.loads(values)
        ret_code,ret_info = post_urlopen(url = roc_url, values=values) 
        #(200, '{"ret":true,"entity_id":"e9caffd63b624f26947f54a30d1dfdfa"}')
        #(200, '{"ret":false,"ret_code":"-100"'})
        print roc_url,'xxxxxxxxxxxxx'
        print ret_code,ret_info
        if ret_code == 200:
            ret_info = json.loads(ret_info)
            if ret_info["ret"] == True:
                response_data = {"ret_code":200,"ret_info":"报障成功！","sn":fault_sn}
                entity_id = ret_info["entity_id"]
                StandardData.objects.filter(std_sn = fault_sn).update(std_entity_id = entity_id)
                for i in range(len(id_faults)):
                    try:
                        id_fault = FaultList.objects.get(id_fault = int(id_faults[i]))
                        ob_machine_fault = MachineFaults(id_fault = id_fault, fault_model = fault_models[i], 
                                              fault_location = fault_locations[i], fault_sn = fault_sn,
                                              fault_num = fault_nums[i], fault_desc = fault_descs[i])
                        ob_machine_fault.save()
                    except Exception,ex:
                        response_data = {"ret_code":500,"ret_info":"报障失败！","sn":fault_sn}
            else:
                response_data = {"ret_code":500,"ret_info":"接口错误，报障失败！","sn":fault_sn}
        else:
            response_data = {"ret_code":500,"ret_info":"报障失败！","sn":fault_sn}
    print response_data["ret_info"]
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    

@csrf_exempt
@login_required
@PermissionVerify()
def powerOn(request):
    response_data = {}
    username = request.POST["auth_username"]
    passowrd = request.POST["auth_password"]
    user = authenticate(username = username, password = passowrd)
    if user is not None: 
        id_brand = SpareBrandList.objects.get(brand_en = "Lenovo")
        if request.user.username == "surecoteam":
            # brand_en = Lenovo
            query = StandardData.objects.filter(id_brand = id_brand).query
        elif request.user.username == "dcitsteam":
            # brand_en = Dell and so on
            query = StandardData.objects.exclude(id_brand = id_brand).query
        else:
            query = StandardData.objects.all().query
        query.group_by = ['std_batch','id_brand_id'] 
        batch_brand = QuerySet(query = query, model = StandardData) 
        cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        response_data = {"ret_code":200,"ret_info":"加电成功！"}
        for item in batch_brand:
            try:
                ob_power_on = PowerOnTime(pt_batch = item.std_batch, id_brand = item.id_brand, 
                                          pt_time = cur_time, id_user = request.user)
                ob_power_on.save()
            except Exception,ex:
                response_data = {"ret_code":500,"ret_info":"加电成功！"}
                continue
    else:
        response_data = {"ret_code":400,"ret_info":"用户名、密码错误！"}
    return HttpResponse(json.dumps(response_data), content_type="application/json")
