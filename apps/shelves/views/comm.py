#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext
from django.db.models import Q
from django.db.models.query import QuerySet
from apps.usermanage.views.permission import PermissionVerify
from apps.usermanage.views.permission import login_required
from apps.workorder.models import IDCList, SpareBrandList, ModelList, FaultList
from apps.shelves.models import CheckCount, StandardData, CheckFailData, PowerOnTime
from plugins.myclass.shelves_models import StandardDataOb, CheckFailDataOb
from plugins.codegit.django_db_oper import queryDB
from plugins.apps.shelves import each_count, std_db2dic, fac_json2dic
from plugins.apps.shelves import resultCount, dataCount
from datetime import date
import requests
import sys
import json
import re
import time
import datetime
import logging
reload(sys)
sys.setdefaultencoding('utf8')
logger = logging.getLogger('shelves')


def shelvesCheckOK(request):
    today = datetime.date.today()
    idate = str(today - datetime.timedelta(days=1))
    year = int(idate.split('-')[0])
    month = int(idate.split('-')[1])
    day = int(idate.split('-')[2])
    result = StandardData.objects.filter(
        std_check_ok=1, std_update__gt=date(year, month, day))
    response_data = {}
    for item in result:
        response_data[item.std_sn] = item.std_check_ok

    kwvars = {
        'title': '上架验收-验收通过',
    }
    return HttpResponse(
        json.dumps(response_data), content_type="application/json")


@login_required()
@PermissionVerify()
def shelvesHelp(request):
    kwvars = {
        'request': request,
        'title': '上架验收-帮助',
    }
    return render_to_response('shelves/help.html', kwvars,
                              RequestContext(request))


@login_required()
@PermissionVerify()
def shelvesHome2(request):
    url = "http://10.134.35.53/api/web.php?batch=purchase-{year_month}".format(
        year_month="2016-10")
    body = requests.get(url)
    kwvars = {
        'request': request,
        'body': body.text,
        'title': '工单系统-基础信息-机房信息列表',
    }
    return render_to_response('shelves/index2.html', kwvars,
                              RequestContext(request))


def get_batch_brand(username):
    id_brand = SpareBrandList.objects.get(brand_en="Lenovo")
    if username == "surecoteam":
        # brand_en = Lenovo
        query = StandardData.objects.filter(id_brand=id_brand).query
    elif username == "dcitsteam":
        # brand_en = Dell and so on
        query = StandardData.objects.exclude(id_brand=id_brand).query
    else:
        query = StandardData.objects.all().query
    query.group_by = ['std_batch', 'id_brand_id']
    batch_brand = QuerySet(query=query, model=StandardData)
    return batch_brand


def get_power_on_list(username):
    id_brand = SpareBrandList.objects.get(brand_en="Lenovo")
    if username == "surecoteam":
        # brand_en = Lenovo
        query = PowerOnTime.objects.filter(id_brand=id_brand)
    elif username == "dcitsteam":
        # brand_en = Dell and so on
        query = PowerOnTime.objects.exclude(id_brand=id_brand)
    else:
        query = PowerOnTime.objects.all()
    return query


def check_poweron(id_user):
    batch_brand = get_batch_brand(id_user.username)
    power_on = get_power_on_list(id_user.username)
    if len(batch_brand) == len(power_on) - 1:
        power_on_status = True
    else:
        #power_on_status = False
	power_on_status = True
	
    return power_on_status


@login_required()
@PermissionVerify()
def shelvesHome(request):
    start = time.time()
    logger.error("start")
    action = request.GET.get("action")
    role = request.user.role.role_en
    username = request.user.username
    idcs = request.POST.getlist("idc")
    brands = request.POST.getlist("brand")
    models = request.POST.getlist("model")
    allidcs = IDCList.objects.filter(idc_enable=True)
    allbrands = SpareBrandList.objects.filter(brand_enable=True).exclude(
        brand_en="sureco").exclude(brand_en="shenma")
    imonth = time.strftime("%Y-%m", time.localtime(time.time()))
    idate = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    year = int(idate.split('-')[0])
    month = int(idate.split('-')[1])
    day = int(idate.split('-')[2])
    cab_api = "http://10.136.130.232/net/info"
    #fac_api = "http://10.142.113.58/check/purchase/index.php?act=data&p=purchase-{imonth}".format(
    fac_api = "http://ias.sogou/check/purchase/index.php?act=data&p=purchase-{imonth}".format(
        imonth=imonth)
    std_api = "http://roc.sogou/pandora/srv_online/loadInterfaceShelvesCheck?type=purchase"
    result_count = {}
    data_count = {}
    print time.time() - start, 'end init'
    try:
        cab_str = requests.request('GET', cab_api).text
        cab = json.loads(cab_str)
    except Exception, ex:
        print 'cab_str:', ex
        cab_str = "{}"
        cab = json.loads(cab_str)
    print time.time() - start, 'end get cab'
    try:
        fac_str = requests.request('GET', fac_api).text
        fac_json = json.loads(fac_str)
        # add
        # fac_fp = open("./data/fac20161031.txt","r")
        # lines = fac_fp.readlines()[0]
        # fac_json = json.loads(lines)
        if str(fac_json) == "f":
            print 'error'
            raise TypeError
    except Exception, ex:
        print 'fac_str:', ex
        fac_str = "{}"
        fac_json = json.loads(fac_str)
    print time.time() - start, 'end get fac_json'

    fac = {}
    if fac_json:
        # print fac_json
        for item in fac_json.values():
            t_fac = fac_json2dic(item=item, cab=cab)
            sn = json.loads(item)["s"]
            fac[sn] = t_fac
    print time.time() - start, 'end fac_json to fac_dic'

    # get std from db
    std_db = StandardData.objects.filter(std_date=idate)
    # if std_db not exist, get from url and insert to db
    std_str = requests.request('GET', std_api).text
    std_json = json.loads(std_str)
    print len(std_json)
    # add
    # std_fp = open("./docs/data/shelves/std20161031.txt","r")
    # lines = std_fp.readlines()[0]
    # std_json = json.loads(lines)
    cur_std_items = [item for item in std_json]
    if not std_db or action == "update":
        std = {}
        try:
            # std_fp = open("std.txt","r")
            # std_fp = open("./docs/data/shelves/std20161031.txt","r")
            # std_fp = open("./docs/data/shelves/std.txt","r")
            # lines = std_fp.readlines()[0]
            # std_json = json.loads(lines)
            for item in std_json:
                std_sn = item
                batch = std_json[item]["batch"]
                rack_id = std_json[item]["rack_id"]
                # brand
                brand = std_json[item]["machine_type"].split(' ')[0]
                # mem
                std_mems = std_json[item]["mem"].split('+')
                std_mems = [
                    x.split('-')[-2] + "*" + x.split('*')[-1] for x in std_mems
                ]
                # if brand == "Lenovo":
                #     std_mems = [
                #         x.split('-')[-1] for x in std_mems
                #     ]
                # else:
                #     std_mems = [
                #         x.split('-')[-2] + "*" + x.split('*')[-1] for x in std_mems
                #     ]
                mem = '+'.join(std_mems)
                # cpu
                cpu = std_json[item]["cpu"]
                # disk
                disk = std_json[item]["disk"]
		#print std_json[item]
                logger.info(json.dumps(std_json[item]))
                
                netcard = std_json[item]["netcard"]
                try:
                    extend = std_json[item]["extend"]
                except Exception,ex:
                    extend = "NA"
                finally:
                    if extend == "N/A":
                        extend = "NA"
                try:
                    bios_v = std_json[item]["bios_v"]
                except Exception,ex:
                    bios_v = ""
                nic_speed = "speed"
                power = std_json[item]["power"]
                # ilo_ip,cable0,cable1
                for ip_item in std_json[item]["ip_detail"]:
                    if ip_item["eth"] == "ethilo":
                        std_ilo = ip_item["ip"]
                    elif ip_item["eth"] == "eth0":
                        std_cable0 = ip_item["cable_id"]
                    elif ip_item["eth"] == "eth1":
                        std_cable1 = ip_item["cable_id"]
                try:
                    ilo_ip = std_ilo
                except Exception, ex:
                    ilo_ip = ""
                try:
                    cable0 = std_cable0
                except Exception, ex:
                    cable0 = ""
                try:
                    cable1 = std_cable1
                except Exception, ex:
                    cable1 = ""
                mac0 = std_json[item]["mac"]["eth0"]
                mac1 = std_json[item]["mac"]["eth1"]
                flag = StandardData.objects.filter(std_sn=std_sn)
                model_en = ' '.join(std_json[item]["machine_type"].split(' ')[1:])
                id_model = ModelList.objects.get(model_en=model_en)
                idc_en = std_json[item]["idc"]
                id_idc = IDCList.objects.get(idc_en=idc_en)
                if flag:
                    flag, desc = StandardDataOb().upall(
                        std_sn=std_sn,
                        id_idc=id_idc,
                        id_model=id_model,
                        std_rack_id=rack_id,
                        std_ilo_ip=ilo_ip,
                        std_cpu=cpu,
                        std_mem=mem,
                        std_disk=disk,
                        std_nic=netcard,
                        std_nic_speed=nic_speed,
                        std_extend=extend,
                        std_bios_v=bios_v,
                        std_power=power,
                        std_mac0=mac0,
                        std_mac1=mac1,
                        std_cable0=cable0,
                        std_cable1=cable1)
                else:
                    flag, desc = StandardDataOb().new(
                        std_sn=std_sn,
                        std_batch=batch,
                        id_idc=id_idc,
                        id_model=id_model,
                        std_rack_id=rack_id,
                        std_ilo_ip=ilo_ip,
                        std_cpu=cpu,
                        std_mem=mem,
                        std_disk=disk,
                        std_nic=netcard,
                        std_nic_speed=nic_speed,
                        std_extend=extend,
                        std_bios_v=bios_v,
                        std_power=power,
                        std_mac0=mac0,
                        std_mac1=mac1,
                        std_cable0=cable0,
                        std_cable1=cable1)
                # print flag,desc
                if flag is True:
                    logger.info("StandardData:success:[%s]%s\nDetail:%s" %
                                (batch, std_sn, desc))
                else:
                    logger.error("StandardData:fail:[%s]%s\nError Log:%s" %
                                 (batch, std_sn, desc))
                # print time.time()-start,'end insertdata to db'
        except Exception, ex:
            print 'insert std_str to db:', ex
    print time.time() - start, 'start get std from db'
    # get std from db ( currentdate and check_fail )
    date_sql = "select std_date from shelves_standarddata where std_check_ok in ( 0,2 ) group by std_date;"
    flag, date_result = queryDB(date_sql)
    if flag:
        date_in = [item[0].strftime("%Y-%m-%d") for item in date_result]
    else:
        date_in = ()
    date_in = tuple(date_in)
    idc_in = [item.encode('utf-8') for item in idcs]
    idc_in = tuple(idc_in)
    # if len(idc_in) == 1:
    #     idc_in = idc_in[0]
    brand_in = [item.encode('utf-8') for item in brands]
    brand_in = tuple(brand_in)
    model_in = [item.encode('utf-8') for item in models]
    model_in = tuple(model_in)
    # if len(brand_in) == 1:
    #     brand_in = brand_in[0]
    sql_where = ""
    if date_in:
        if len(date_in) == 1:
            sql_where = "{sql_where} and std.std_date = '{date_in}'".format(
                sql_where=sql_where, date_in=date_in[0])
        elif len(date_in) > 1:
            sql_where = "{sql_where} and std.std_date in {date_in}".format(
                sql_where=sql_where, date_in=date_in)
    if idc_in:
        if len(idc_in) == 1:
            sql_where = "{sql_where} and idc.idc_en = '{idc_in}'".format(
                sql_where=sql_where, idc_in=idc_in[0])
        else:
            sql_where = "{sql_where} and idc.idc_en in {idc_in}".format(
                sql_where=sql_where, idc_in=idc_in)
    if brand_in:
        if len(brand_in) == 1:
            sql_where = "{sql_where} and brand.brand_en = '{brand_in}'".format(
                sql_where=sql_where, brand_in=brand_in[0])
        else:
            sql_where = "{sql_where} and brand.brand_en in {brand_in}".format(
                sql_where=sql_where, brand_in=brand_in)
    if model_in:
        if len(model_in) == 1:
            sql_where = "{sql_where} and model.model_en = '{model_in}'".format(
                sql_where=sql_where, model_in=model_in[0])
        else:
            sql_where = "{sql_where} and model.model_en in {model_in}".format(
                sql_where=sql_where, model_in=model_in)
    if username == "surecoteam":
        # brand_en = Lenovo
        sql_where = "{sql_where} and brand_en = 'Lenovo'".format(
            sql_where=sql_where)
    elif username == "dcitsteam":
        # brand_en = Dell and so on
        sql_where = "{sql_where} and brand_en in ('AMAX','Dell')".format(
            sql_where=sql_where)
    if sql_where:
        sql_where = sql_where[4:]
    if date_in:
        std_db_sql = """
select std_date,std_sn,std_batch,concat(brand_en,' ',model_en),std_rack_id,
       idc_en,std_ilo_ip,std_cpu,std_mem,std_disk,std_nic,std_nic_speed,
       std_power,std_raid,std_mac0,std_mac1,std_cable0,std_cable1,std_ilo_st,
       std_real_exist,std_onetime_pass,std_check_ok,std_bios_v,std_start,
       std_entity_id,std_extend
from shelves_standarddata std
left join workorder_idclist idc on (std.id_idc_id = idc.id_idc)
left join workorder_sparebrandlist brand on (std.id_brand_id = brand.id_brand)
left join workorder_modellist model on (std.id_model_id = model.id_model)
where {sql_where}
""".format(sql_where=sql_where)
        logger.info(std_db_sql)
        flag, std_db = queryDB(std_db_sql)
    else:
        std_db = ()
    print time.time() - start, 'end get std from db'
    std = {}
    # get std from db ( currentdate and check_fail )
    allmodels = {}
    if flag:
        for item in std_db:
            std_sn = item[1]
            t_std = std_db2dic(item=item)
            std[std_sn] = t_std
            if t_std["model"] not in allmodels:
                allmodels[t_std["model"]] = t_std["model"]
        print time.time() - start, 'end std_db to std_dic'

    #cur_std_model = [std_json[item]["machine_type"] for item in std_json]
    #allmodels = {}
    #for model in cur_std_model:
    #    if model not in allmodels:
    #        allmodels[model] = ' '.join(model.split(' ')[1:])

    for item in std:
        brand = std[item]["model"].split(" ")[0]
        idc = std[item]["idc"]
        batch = re.sub("\.", "-", std[item]["batch"])
        tmp_nodata = {}
        tmp_fail = {}
        tmp_ok = {}
        if std[item]["std_check_ok"] == 1:
            # ok
            if item in cur_std_items:
                std[item]["installed"] = 0
            else:
                std[item]["installed"] = 1
            result_count = resultCount(result_count, batch, idc, brand,
                                       "ok")
            data_count = dataCount(
                data_count=data_count,
                t_result=std[item],
                batch=batch,
                st="ok")
        elif item not in fac:
            # nodata
            result_count = resultCount(result_count, batch, idc, brand,
                                       "fail")
            data_count = dataCount(
                data_count=data_count,
                t_result=std[item],
                batch=batch,
                st="nodata")
        else:
            # checking
            result_count, t_result = each_count(
                result_count=result_count,
                fac_item=fac[item],
                std_item=std[item],
                sn=item,
                batch=batch,
                idc=idc,
                brand=brand,
                cur_std_items=cur_std_items)
            data_count = dataCount(
                data_count=data_count,
                t_result=t_result,
                batch=batch,
                st=t_result["stat"])
    print time.time() - start, 'end check data'
    for item in result_count:
        result_count[item]["fail_sum"] = 0
        for iitem in result_count[item]["idc_count"]:
            result_count[item]["fail_sum"] += result_count[item]["idc_count"][iitem]["fail"]
            result_count[item]["idc_count"][iitem]["percent"] = result_count[item]["idc_count"][iitem]["ok"]*100/result_count[item]["idc_count"][iitem]["sum"]
        for iitem in result_count[item]["brand_count"]:
            result_count[item]["brand_count"][iitem]["percent"] = result_count[item]["brand_count"][iitem]["ok"]*100/result_count[item]["brand_count"][iitem]["sum"]
    print time.time() - start, 'end count data'
    fault_list = FaultList.objects.all()
    # if list is NULL poweron_status is True
    poweron_status = check_poweron(request.user)
    kwvars = {
        'request': request,
        'poweron_status': poweron_status,
        'data_count': data_count,
        'result_count': result_count,
        'idcs': idcs,
        'allidcs': allidcs,
        'models': models,
        'allmodels': allmodels,
        'brands': brands,
        'allbrands': allbrands,
        "fault_list": fault_list,
    }
    print time.time() - start, 'end'
    return render_to_response('shelves/index.html', kwvars,RequestContext(request))
