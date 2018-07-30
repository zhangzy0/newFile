#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required

from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
from apps.workorder.models import DailyInfo,RepairInfo,RepairInfoFault
from apps.workorder.models import SpareList
import simplejson as json
import logging
logger = logging.getLogger('workorder')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def Home(request):
    id_user = request.user
    try:
        # idcer 显示所管理机房的信息
        if id_user.role.role_en == "idcer":
            allDailyInfo_unfinish = []
            allRepairInfo_unfinish = []
            id_idcs = id_user.idc_users.all()
            id_idcs = [int(idc.id_idc) for idc in id_idcs]
            id_idcs = tuple(id_idcs)
            if len(id_idcs) == 1: sql_where = 'id_idc_id = %s' %(id_idcs[0])
            else: sql_where = 'id_idc_id in '+str(id_idcs)
            sql_where2 = sql_where + ' and id_st_id in (4,6,8,11)'
            #allRepairInfo_waitprocess = RepairInfo.objects.exclude(id_st = 1).extra(where=[sql_where]).order_by('-re_create_time')
            #print sql_where,sql_where2
            allRepairInfo_waitaccept = RepairInfo.objects.filter(id_st = 7).extra(where=[sql_where]).order_by('-re_create_time')
            allDailyInfo_waitaccept = DailyInfo.objects.filter(id_st = 7).extra(where=[sql_where]).order_by('-dainfo_create_time')
            allRepairInfo_waitprocess = RepairInfo.objects.all().extra(where=[sql_where2]).order_by('-re_create_time')
            allDailyInfo_waitprocess = DailyInfo.objects.all().extra(where=[sql_where2]).order_by('-dainfo_create_time')
            allRepairInfo_waitcheck = RepairInfo.objects.filter(id_st = 9).extra(where=[sql_where]).order_by('-re_create_time')
            allDailyInfo_waitcheck = DailyInfo.objects.filter(id_st = 9).extra(where=[sql_where]).order_by('-dainfo_create_time')
            t_Repair = []
            for item in allRepairInfo_waitaccept:
                tmp = [item,RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo)]
                t_Repair.append(tmp)
            allRepairInfo_waitaccept = t_Repair
            t_Repair = []
            for item in allRepairInfo_waitprocess:
                tmp = [item,RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo)]
                t_Repair.append(tmp)
            allRepairInfo_waitprocess = t_Repair
            t_Repair = []
            for item in allRepairInfo_waitcheck:
                tmp = [item,RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo)]
                t_Repair.append(tmp)
            allRepairInfo_waitcheck = t_Repair
            kwvars = {
                'request':request,
                'title':'工单系统-主页',
                'title_content':'我的工作',
                'allRepairInfo_waitaccept':allRepairInfo_waitaccept,
                'allDailyInfo_waitaccept':allDailyInfo_waitaccept,
                'allRepairInfo_waitprocess':allRepairInfo_waitprocess,
                'allDailyInfo_waitprocess':allDailyInfo_waitprocess,
                'allRepairInfo_waitcheck':allRepairInfo_waitcheck,
                'allDailyInfo_waitcheck':allDailyInfo_waitcheck,
            }
            return render_to_response('workorder/index_idcer.html',kwvars,RequestContext(request))

        # sogouer 显示所有机房的信息
        #elif id_user.role.role_en == "sogouer" or id_user.role.role_en == "Admin":
        else:
            sql_where = 'id_st_id in (4,6,8,11)'
            allRepairInfo_waitaccept = RepairInfo.objects.filter(id_st = 7).order_by('-re_create_time')
            allDailyInfo_waitaccept = DailyInfo.objects.filter(id_st = 7).order_by('-dainfo_create_time')
            allRepairInfo_waitprocess = RepairInfo.objects.all().extra(where=[sql_where]).order_by('-re_create_time')
            allDailyInfo_waitprocess = DailyInfo.objects.all().extra(where=[sql_where]).order_by('-dainfo_create_time')
            allRepairInfo_waitcheck = RepairInfo.objects.filter(id_st = 9).order_by('-re_create_time')
            allDailyInfo_waitcheck = DailyInfo.objects.filter(id_st = 9).order_by('-dainfo_create_time')
            t_Repair = []
            for item in allRepairInfo_waitaccept:
                tmp = [item,RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo)]
                t_Repair.append(tmp)
            allRepairInfo_waitaccept = t_Repair
            t_Repair = []
            for item in allRepairInfo_waitprocess:
                tmp = [item,RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo)]
                t_Repair.append(tmp)
            allRepairInfo_waitprocess = t_Repair
            t_Repair = []
            for item in allRepairInfo_waitcheck:
                tmp = [item,RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo)]
                t_Repair.append(tmp)
            allRepairInfo_waitcheck = t_Repair
            kwvars = {
                'request':request,
                'title':'工单系统-主页',
                'title_content':'我的工作',
                'allRepairInfo_waitaccept':allRepairInfo_waitaccept,
                'allDailyInfo_waitaccept':allDailyInfo_waitaccept,
                'allRepairInfo_waitprocess':allRepairInfo_waitprocess,
                'allDailyInfo_waitprocess':allDailyInfo_waitprocess,
                'allRepairInfo_waitcheck':allRepairInfo_waitcheck,
                'allDailyInfo_waitcheck':allDailyInfo_waitcheck,
            }
            return render_to_response('workorder/index_sogouer.html',kwvars,RequestContext(request))
    except Exception,ex:
        kwvars = {
            'request':request,
            'title':'工单系统-主页',
            'title_content':'我的工作',
        }
        return render_to_response('workorder/index.html',kwvars,RequestContext(request))


@login_required()
def test(request):
    brand_list = {}
    #t_brand_list = SpareBrandList.objects.all()
    #for item in t_brand_list:
    #    id_brand = str(item.id_brand)
    #    brand_list[id_brand] = {}
    #    brand_list[id_brand]["name"] = str(item.brand_en)
    #    t_spare_list = SpareList.objects.filter(id_brand = item)
    #    tmp_spare_list = []
    #    for iitem in t_spare_list:
    #        tmp_str = "{txt:'%s',val:'%s'}" %(int(iitem.id_spare),str(iitem.spare_en))
    #        tmp_spare_list.append(tmp_str)
    #        #tmp_spare_list.append({"txt":int(iitem.id_spare),"val":str(iitem.spare_en)})
    #    brand_list[id_brand]["vals"] = tmp_spare_list
    #    break
    t_spare_list = SpareList.objects.filter(id_brand = 2)
    result = []
    for item in t_spare_list:
        print item
        result.append({"txt":int(item.id_spare),"val":str(item.spare_en)})
    print result
    return HttpResponse(json.dumps(result,ensure_ascii = False))
    #if request.method == "POST":
    #    print request.FILES
    #    
    #    pass
    #kwvars = {
    #    'request':request,
    #    'title':'Home',
    #    'postUrl':'/workorder/test/',
    #}
    #return render_to_response('workorder/test.html',kwvars,RequestContext(request))
