#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.usermanage.views.permission import PermissionVerify
from apps.workorder.models import IDCList, SpareBrandList, ModelList
from apps.shelves.models import CheckCount, StandardData, CheckFailData
from plugins.myclass.shelves_models import StandardDataOb, CheckFailDataOb
from plugins.codegit.django_db_oper import queryDB
from plugins.apps.shelves import check_data
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

@login_required
@PermissionVerify()
def shelvesCheckCount(request):
    #{batch:{name:,val:}}
    q_year = request.GET.get("year")
    q_quarter = request.GET.get("quarter")
    q_month = request.GET.get("month")
    sql_where = ""
    counts = CheckCount.objects.all()
    checked = "all"
    if q_year and q_quarter and q_month:
        mycounts = CheckCount.objects.filter(cc_batch__contains = q_year).filter(cc_batch__contains = q_quarter).filter(cc_batch__contains = "_"+q_month)
        checked = "{year}_{quarter}_{month}".format(year=q_year,quarter=q_quarter,month=q_month)
    elif q_year and q_quarter: 
        mycounts = CheckCount.objects.filter(cc_batch__contains = q_year).filter(cc_batch__contains = q_quarter)
        checked = "{year}_{quarter}".format(year=q_year,quarter=q_quarter)
    elif q_year: 
        mycounts = CheckCount.objects.filter(cc_batch__contains = q_year)
        checked = q_year
    else:
        mycounts = CheckCount.objects.all()
    all_count = {}
    fail_detail = {}
    years = []
    quarters = []
    months = []
    for item in counts:
        batch_sor = item.cc_batch
        year = re.match(r"(\d{4})Q.*",batch_sor).groups()[0]
        quarter = re.match(r"\d{4}(Q\d).*",batch_sor).groups()[0]
        month = re.match(r"\d{4}.*?_(\d{2}).*",batch_sor).groups()[0]
        if year not in years:years.append(year)
        if quarter not in quarters:quarters.append(quarter)
        if month not in months:months.append(month)
    for item in mycounts:
        batch_sor = item.cc_batch
        batch = re.sub("\.","-",item.cc_batch)
        if batch not in fail_detail:
            fail_detail[batch] = {}
        if batch not in all_count:
            all_count[batch] = {}
            all_count[batch]["name"] = batch_sor
            all_count[batch]["val"] = []
        count_info = {}
        try:
            error_fix = CheckFailData.objects.filter(ck_batch = batch_sor, id_brand = item.id_brand)
        except Exception,ex:
            print ex
            continue 
        count_info["id_brand"] = item.id_brand
        count_info["cc_sum"] = item.cc_sum
        if item.cc_start_time and item.cc_start_time:
            take_times = item.cc_end_time - item.cc_start_time
            take_times = take_times.total_seconds()/60/60
            take_times = int(round(take_times))
        else:
            take_times = "NULL"
        count_info["cc_take_times"] = take_times
        count_info["cc_onetime_pass"] = item.cc_onetime_pass
        count_info["cc_failcount"] = item.cc_failcount
        count_info["cc_last_time"] = str(item.cc_end_time)
        sql = "select pt_time from shelves_powerontime where pt_batch = '{pt_batch}' and id_brand_id = {id_brand}".format(pt_batch = batch_sor, id_brand = item.id_brand.id_brand)
        flag, result = queryDB(sql)
        if flag and result:
            count_info["cc_poweron_time"] = result[0][0]
        else:
            count_info["cc_poweron_time"] = None
        all_count[batch]["val"].append(count_info)
        # print batch
        # print error_fix
        fail_detail[batch][item.id_brand.brand_en] = error_fix
    # tree info
    batchs = [ re.match(r"(\d{4}Q\d{1})\.\d{1,}_(\d{2}).*",item.cc_batch).groups() for item in counts]
    batchs = list(set([ "{i0}{i1}".format(i0 = item[0], i1 = item[1]) for item in batchs ]))
    all_children = []
    tree_info = [{"name":"统计", "children":all_children, "t":"all", "open":"true", "url":"?all=all","target":"_self"}]
    for year in years:
        year_children = []
        item_year = { "name":"{year}年".format(year = year),"open":"true","url":"?year={year}".format(year=year),"t":year, "target":"_self", "children":year_children}
        for quarter in quarters:
            quarter_children = []
            year_quarter = "{year}{quarter}".format(year = year, quarter = quarter)
            batchs_year_quarter = [ item[0:6] for item in batchs ]
            if year_quarter in batchs_year_quarter:
                tmp_child = { "name":quarter, "url":"?year={year}&quarter={quarter}".format(year=year, quarter=quarter), "t":"{year}_{quarter}".format(year=year, quarter=quarter), "target":"_self", "children":quarter_children }
                year_children.append(tmp_child)
            for month in months:
                year_quarter_month = "{year}{quarter}{month}".format(year = year, quarter = quarter,month = month)
                if year_quarter_month in batchs:
                    tmp_child = {"name":"{month}月".format(month = int(month)),"url":"?year={year}&quarter={quarter}&month={month}".format(year=year, quarter=quarter, month=month),"t":"{year}_{quarter}_{month}".format(year = year, quarter = quarter,month = month), "target":"_self",}
                    quarter_children.append(tmp_child)
        all_children.append(item_year)
    tree_info = json.dumps(tree_info)
    kwvars = {
        'tree_info':tree_info,
        'checked':checked,
        'all_count':all_count,
        'fail_detail':fail_detail,
        'request':request,
        'title':'上架验收-统计查询',
    }
    return render_to_response('shelves/checkcount.html',kwvars,RequestContext(request))

