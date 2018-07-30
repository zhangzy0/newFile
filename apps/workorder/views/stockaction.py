#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required
from django.views.decorators.csrf import csrf_exempt

from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
from apps.workorder.models import StockInout,StockList, SpareBrandList, SpareList
from apps.workorder.models import DailyInfo,RepairInfo,DailywoAttach,Remark
from apps.workorder.models import Process,RepairInfoFault
from apps.workorder.models import IDCList
from apps.usermanage.models import User
from apps.workorder.forms import StockInoutAddForm,StockInoutEditForm
from plugins.myclass.workorder_models import SpareOb, StockOb, StockInoutOb
#import json
from django.db.models import Q
import simplejson as json
import logging
logger = logging.getLogger('workorder')
area_dic = {"BJ":"北京","GD":"广东","NM":"内蒙","":"-"}


#@login_required()
#@IpaddressAcl()
#@PermissionVerify()

@csrf_exempt
def apiDelStocklogs(request):
    print request.POST
    ret_code = 200
    ret_info = "删除成功"
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        for id in ids:
            try:
                StockInout.objects.get(id_stinout = int(id)).delete()
            except Exception,ex:
                print ex
                ret_code = 500
                ret_info = "删除失败"
                
    response_data = {"ret_code":ret_code,"ret_info": ret_info ,"sn":"123"}
    return HttpResponse(json.dumps(response_data), content_type="application/json")
