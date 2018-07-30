#!/usr/bin/env python
#-*- coding: utf-8 -*-
""" rocshow 的视图
Author:
    liuzhen2104300@sogou-inc.com
Date:
    2016-03-03
Usage:
    功能是什么呢？
Version:
    V1.0 2016-03-03 init
"""

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import PermissionVerify
from apps.usermanage.views.permission import login_required
from apps.workorder.models import IDCList,ModelList,FaultList
from plugins.common.db import query_asset_sql
from plugins.codegit.date_week_month import getNumDays
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import logging
logger = logging.getLogger('rocshow')


@login_required()
@PermissionVerify()
def dashboard(request):
    kwvars = {
        'request':request,
        'title':'工单系统-基础信息-机房信息列表',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('rocshow/index.html',kwvars,RequestContext(request))

@login_required()
@PermissionVerify()
def faultSearch(request):
    form = {}
    form["idc_list"] = IDCList.objects.filter(idc_enable = True )
    form["model_list"] = ModelList.objects.filter(model_enable = True )
    form["fault_list"] = FaultList.objects.filter(fault_enable = True )
    disk_vender_list_sql = "select vender from repair_record group by vender;"
    form["disk_vender_list"] = query_sql(disk_vender_list_sql)
    form["disk_vender_list"] = [ vender[0] for vender in form["disk_vender_list"] if vender[0]]
    if request.method == "POST":
        q_datefrom = ""
        q_dateto = ""
    else:
        q_datefrom = str(getNumDays(n=365))
        #q_datefrom = str(getNumDays(n=300))
        q_dateto = str(getNumDays())
    q_datefrom = str(getNumDays(n=365))
    #q_datefrom = str(getNumDays(n=300))
    q_dateto = str(getNumDays())
    print q_datefrom,q_dateto
    charts = {}
    if request.method == "POST":
        sql_colum_dict = {"idc":"substring_index(rack_id,'-',2)","fault":"fault_type","model":"machine_model","disk_vender":"vender"}
        print request.POST
        idc_list = request.POST.getlist("idc")
        model_list = request.POST.getlist("model")
        fault_list = request.POST.getlist("fault")
        disk_vender_list = request.POST.getlist("disk_vender")
        order_list = request.POST.getlist("order")
        if not order_list: order_list=["idc","model","fault"]
        sql_column = ""
        sql_group = ""
        for item in order_list:
           sql_column = "{0}{1},'&',".format(sql_column, sql_colum_dict[item])
           sql_group = "{0}{1},".format(sql_group, sql_colum_dict[item])
        sql_where = ""
        if idc_list : 
            idc_list = [x.encode('utf8') for x in idc_list]
            if len(idc_list) == 1:idc_list="('%s')" %(idc_list[0]) 
            else: idc_list = tuple(idc_list)
            sql_where = sql_where +"%s in %s and " %(sql_colum_dict["idc"],idc_list)
        if model_list : 
            model_list = [x.encode('utf8') for x in model_list]
            if len(model_list) == 1:model_list="('%s')" %(model_list[0]) 
            else: model_list = tuple(model_list)
            sql_where = sql_where +"%s in %s and " %(sql_colum_dict["model"],model_list)
        if fault_list : 
            fault_list = [x.encode('utf8') for x in fault_list]
            if len(fault_list) == 1:fault_list="('%s')" %(fault_list[0]) 
            else: fault_list = tuple(fault_list)
            sql_where = sql_where +"%s in %s and " %(sql_colum_dict["fault"],fault_list)
        if disk_vender_list:
            disk_vender_list = [x.encode('utf8') for x in disk_vender_list]
            if len(disk_vender_list) == 1:disk_vender_list="('%s')" %(disk_vender_list[0])
            else: disk_vender_list = tuple(disk_vender_list)
            sql_where = sql_where +"%s in %s and " %(sql_colum_dict["disk_vender"], disk_vender_list)
        if sql_where:
            sql_where = sql_where + "substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) <= '%s'" %(q_datefrom,q_dateto)
            #sql = "select concat(%s),count(id) from repair_record where %s group by %s order by count(id) desc ;" %(sql_column[:-5],sql_where[:-4],sql_group[:-1])
            sql = "select concat(%s),count(id) from repair_record where %s group by %s order by count(id) desc ;" %(sql_column[:-5],sql_where,sql_group[:-1])
        else:
            sql = "select concat(%s),count(id) from repair_record where substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) <= '%s' group by %s order by count(id) desc;" %(sql_column[:-5],q_datefrom,q_dateto,sql_group[:-1])
    else:
        sql = "select count(id),concat(substring_index(rack_id,'-',2),'&',fault_type) from repair_record where substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) <= '%s' group by substring_index(rack_id,'-',2),fault_type order by count(id) desc ;" %(q_datefrom,q_dateto)
    print sql
    result = query_sql(sql)
    form["table_list"] = result
    idc = {'all':{'710':{'disk':{'1','deatail'}}}}
    form["idc"] = idc
    kwvars = {
        'form':form,
        'charts':charts,
        'request':request,
        'title':'工单系统-基础信息-机房信息列表',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('rocshow/faultSearch.html',kwvars,RequestContext(request))

@login_required()
@PermissionVerify()
def faultCount(request):
    form = {}
    form["idc_list"] = IDCList.objects.filter(idc_enable = True )
    form["model_list"] = ModelList.objects.filter(model_enable = True )
    form["fault_list"] = FaultList.objects.filter(fault_enable = True )
    if request.method == "POST":
        q_datefrom = ""
        q_dateto = ""
    else:
        q_datefrom = str(getNumDays(n=7))
        ##q_datefrom = str(getNumDays(n=300))
        q_dateto = str(getNumDays())
        #q_datefrom = "2016-10-24"
        #q_dateto = "2016-10-30"
    print q_datefrom,q_dateto
    idc_faultcount = []
    fault_count = {}
    fault_count["name"] = "所有"
    fault_count["name_en"] = "all"
    sql = "select machine_model, count(id) '总数',"
    for fault in form["fault_list"]:
        sql = sql + " sum(case fault_type when '%s' then 1 else 0 end ) '%s'," %(fault.fault_en,fault.fault_cn)
    if q_datefrom and q_dateto:
        #sql = sql[:-1] + " from repair_record where substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) <= '%s' group by machine_model order by count(id) desc;" %(q_datefrom,q_dateto)
        sql = sql[:-1] + " from repair_record where substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) <= '%s' and  fault_type not in ('unknown','down','chongqi','fsallfail','second_fsallfail','second_down','manual','ilo_cfg','bios_cfg','agent_ex','sys_fs','halfnet_unreachable','plugin_ex') group by machine_model order by count(id) desc;" %(q_datefrom,q_dateto)
    else:
        #sql = sql[:-1] + " from repair_record group by machine_model order by count(id) desc;"
        sql = sql[:-1] + " from repair_record where  fault_type not in ('unknown','down','chongqi','fsallfail','second_fsallfail','second_down','manual','ilo_cfg','bios_cfg','agent_ex','sys_fs','halfnet_unreachable','plugin_ex') group by machine_model order by count(id) desc;"
    print sql
    result = query_sql(sql)
    fault_count["result"] = result
    idc_faultcount.append(fault_count)
    for idc in form["idc_list"]:
        fault_count = {}
        fault_count["name"] = idc.idc_cn
        fault_count["name_en"] = idc.idc_en
        sql = "select machine_model, count(id) '总数',"
        for fault in form["fault_list"]:
            sql = sql + " sum(case fault_type when '%s' then 1 else 0 end ) '%s'," %(fault.fault_en,fault.fault_cn)
        if q_datefrom and q_dateto:
            #sql = sql[:-1] + " from repair_record where substring_index(rack_id,'-',2) = '%s' and substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) <= '%s' group by machine_model order by count(id) desc;" %(idc.idc_en,q_datefrom,q_dateto)
            sql = sql[:-1] + " from repair_record where substring_index(rack_id,'-',2) = '%s' and substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) <= '%s' and  fault_type not in ('unknown','down','chongqi','fsallfail','second_fsallfail','second_down','manual','ilo_cfg','bios_cfg','agent_ex','sys_fs','halfnet_unreachable','plugin_ex') group by machine_model order by count(id) desc;" %(idc.idc_en,q_datefrom,q_dateto)
        else:
            #sql = sql[:-1] + " from repair_record where substring_index(rack_id,'-',2) = '%s' group by machine_model order by count(id) desc;" %(idc.idc_en)
            sql = sql[:-1] + " from repair_record where substring_index(rack_id,'-',2) = '%s' and  fault_type not in ('unknown','down','chongqi','fsallfail','second_fsallfail','second_down','manual','ilo_cfg','bios_cfg','agent_ex','sys_fs','halfnet_unreachable','plugin_ex') group by machine_model order by count(id) desc;" %(idc.idc_en)
        print sql
        result = query_sql(sql)
        fault_count["result"] = result
        idc_faultcount.append(fault_count)
    form["idc_fault"] = idc_faultcount
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-机房信息列表',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('rocshow/faultCount.html',kwvars,RequestContext(request))

@login_required()
@PermissionVerify()
def faultDetail(request):
    form = {}
    form["idc_list"] = IDCList.objects.filter(idc_enable = True )
    form["model_list"] = ModelList.objects.filter(model_enable = True )
    form["fault_list"] = FaultList.objects.filter(fault_enable = True )
    if request.method == "POST":
        q_datefrom = ""
        q_dateto = ""
    else:
        q_datefrom = str(getNumDays(n=300))
        q_dateto = str(getNumDays())
    print q_datefrom,q_dateto
    idc_faultdetail = []
    fault_detail = {}
    fault_detail["name"] = "所有"
    fault_detail["name_en"] = "all"
    if q_datefrom and q_dateto:
        sql = "select substring_index(rack_id,'-',2) JF,start_time,rack_id,machine_model,fault_type,fault_desc from repair_record where substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) <= '%s' order by start_time desc " %(q_datefrom,q_dateto)
    else:
        sql = "select substring_index(rack_id,'-',2) JF,start_time,rack_id,machine_model,fault_type,fault_desc from repair_record order by start_time desc "
    result = query_sql(sql)
    fault_detail["result"] = result
    idc_faultdetail.append(fault_detail)
    for idc in form["idc_list"]:
        fault_detail = {}
        fault_detail["name"] = idc.idc_cn
        fault_detail["name_en"] = idc.idc_en
        if q_datefrom and q_dateto:
            sql = "select substring_index(rack_id,'-',2) JF,start_time,rack_id,machine_model,fault_type,fault_desc from repair_record where substring_index(rack_id,'-',2) = '%s'  and substring_index(start_time,' ',1) >= '%s' and substring_index(start_time,' ',1) < '%s' order by start_time desc " %(idc.idc_en,q_datefrom,q_dateto)
        else:
            sql = "select substring_index(rack_id,'-',2) JF,start_time,rack_id,machine_model,fault_type,fault_desc from repair_record where substring_index(rack_id,'-',2) = '%s' order by start_time desc " %(idc.idc_en)
        print sql
        result = query_sql(sql)
        fault_detail["result"] = result
        idc_faultdetail.append(fault_detail)
    form["idc_detail"] = idc_faultdetail
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-机房信息列表',
        #'postUrl':'/workorder/idc/list/',
    }
    #select substring_index(rack_id,'-',2) JF,rack_id,machine_model,fault_type,fault_desc from repair_record
    return render_to_response('rocshow/faultDetail.html',kwvars,RequestContext(request))


@login_required()
@PermissionVerify()
def error500(request):
    kwvars = {
        'request':request,
        'title':'工单系统-基础信息-机房信息列表',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('rocshow/ajax/page_500.html',kwvars,RequestContext(request))


@login_required()
@PermissionVerify()
def error404(request):
    kwvars = {
        'request':request,
        'title':'工单系统-基础信息-机房信息列表',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('rocshow/ajax/page_404.html',kwvars,RequestContext(request))
