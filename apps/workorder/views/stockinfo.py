#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required
from django.db.models.query import QuerySet

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


@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockLog(request):
    mList = StockInout.objects.all().order_by('-stio_create_time')
    lst = SelfPaginator(request,mList, 15)
    query = StockInout.objects.all().query
    query.group_by = ['id_user_id',]
    user_list = QuerySet(query = query, model = StockInout)
    kwvars = {
        'lPage':lst,
        'request':request,
        'user_list':user_list,
        'title':'工单系统-备件管理-备件记录查询',
        'title_content':'备件日志查询',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('workorder/stockLog.html',kwvars,RequestContext(request))

#@login_required()
#@IpaddressAcl()
#@PermissionVerify()
def dataGetnewspare(request):
    # 0, no use bad
    # 1, no use good
    # 2, use good
    # 3, use bad
    # 4, no need
    if request.method == "GET":
        # get all new stock
        try:
            id_spare = request.GET["id_spare"]
            id_idc = request.GET["idc"]
            id_idc_ob = IDCList.objects.get(id_idc = id_idc)
            id_repairwo = request.GET["id_repairwo"]
            id_refault = request.GET["id_refault"]
            stock_area = id_idc_ob.idc_en.split('-')[0]
            mList = StockList.objects.filter(id_spare = id_spare,stock_area = stock_area, stock_st = 1)
        except Exception,ex:
            print ex
            mList = StockList.objects.all()
        kwvars = {
            'lPage':mList,
            'request':request,
            'title':'工单系统-备件管理-备件替换',
            'title_content':'选择替换的备件',
            'postUrl':'/workorder/repairwo/getnewspare/',
        }
        return render_to_response('workorder/dataGetnewspare.html',kwvars,RequestContext(request))
    else:
        # replace bad stock to good
        try:
            id_user = request.user
            id_stocks = []
            id_repairwo = request.POST["id_repairwo"]
            id_stock = request.POST["id_stock"]           # current
            id_refault = request.POST["id_refault"]
            id_spare = request.POST["id_spare"]
            stock_sn_old = request.POST["stock_sn_old"]   # old_stock
            stock_sn_new = request.POST["stock_sn_new"]   # new_stock
            RepairInfoFault.objects.filter(id_refault = id_refault).update(refault_spare_sn_new = id_stock)
            # new stock status to good-using
            #print "change id_stock status to 2"  # using
            StockList.objects.filter(id_stock = id_stock).update(stock_st = 2)
            id_reinfo = RepairInfo.objects.get(id_reinfo = id_repairwo)
            id_spare = SpareList.objects.get(id_spare = id_spare)
            id_stocks.append(id_stock)


            flag = StockList.objects.filter(stock_sn = stock_sn_old).update(stock_st = 0)
            if flag == 0:
                print "insert old stock to stocklist status to 0"  # bad
                stock_area = id_reinfo.id_idc.idc_en.split('-')[0]
                flag,desc = StockOb().new(stock_area = stock_area, id_spare = id_spare, stock_sn = stock_sn_old, stock_st = 0)
                tmp_stock = StockList.objects.get(stock_sn = stock_sn_old)
                stio_descript = "线上坏件导入，状态：坏件-未使用"
                flag,desc = StockInoutOb().new(id_spare = id_spare, id_reinfo = id_reinfo, stio_type = "坏件导入", stio_descript = stio_descript, id_user = id_user, id_stock = tmp_stock.id_stock )

            # current stock
            StockList.objects.filter(id_stock = id_stock).update(stock_st = 2)
            stio_descript = "状态变更为：好件-使用中"
            flag,desc = StockInoutOb().new(id_spare = id_spare, id_reinfo = id_reinfo, stio_type = "变更", stio_descript = stio_descript, id_user = id_user, id_stock = int(id_stock) )

            if stock_sn_new:
                StockList.objects.filter(stock_sn = stock_sn_new).update(stock_st = 1)
                tmp_stock = StockList.objects.get(stock_sn = stock_sn_new)
                id_stocks.append(tmp_stock.id_stock)
                stio_descript = "状态变更为：好件-未使用"
                flag,desc = StockInoutOb().new(id_spare = id_spare, id_reinfo = id_reinfo, stio_type = "变更", stio_descript = stio_descript, id_user = id_user, id_stock = tmp_stock.id_stock )

            # replace log
            flag,desc = StockInoutOb().new(id_spare = id_spare, id_reinfo = id_reinfo, stio_type = "替换", id_user = id_user, id_stock = id_stocks )
        except Exception,ex:
            print ex
        kwvars = {}
        return HttpResponseRedirect('/workorder/repairwo/view/{id_repairwo}'.format(id_repairwo = id_repairwo))


def getBrandStock( brand = None):
    brand_list = {}
    if brand is None:
        t_brand_list = SpareBrandList.objects.all()
    else:
        t_brand_list = SpareBrandList.objects.filter(Q(brand_en = "sureco") | Q(brand_en = "shenma"))
    for item in t_brand_list:
        id_brand = str(item.id_brand)
        brand_list[id_brand] = {}
        brand_list[id_brand]["name"] = str(item.brand_cn)
        t_spare_list = SpareList.objects.filter(id_brand = item)
        tmp_spare_list = []
        for iitem in t_spare_list:
            tmp_spare_list.append({"val":int(iitem.id_spare),"txt":str(iitem.spare_en)})
        brand_list[id_brand]["vals"] = tmp_spare_list
    return brand_list

@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockNew(request):
    message = ""
    if request.method == "POST":
        try:
            id_user = request.user
            id_spare_id = request.POST["id_spare"]
            id_spare = SpareList.objects.get(id_spare = int(id_spare_id))
            stock_sn = request.POST["stock_sn"]
            stock_area = request.POST["stock_area"]
            stock_st = request.POST["stock_st"]
            flag,desc = StockOb().new(stock_area = stock_area, id_spare = id_spare, stock_sn = stock_sn, stock_st = stock_st)
            ob_stock = StockList.objects.get(stock_sn = stock_sn)
            if flag:
                message = "添加成功,继续添加吧"
            else:
                message = "添加失败,请检查SN号是否重复"
            print flag,desc
            flag,desc = StockInoutOb().new(id_spare = id_spare, stio_type = "入库", id_user = id_user, id_stock = ob_stock.id_stock)
            print flag,desc
        except Exception,ex:
            print ex
            message = "添加失败"
    idc_list = IDCList.objects.filter(idc_enable = True)
    brand_list = getBrandStock( brand = "thirdpart" )
    kwvars = {
        'request':request,
        'message':message,
        'brand_list':brand_list,
        'idc_list':idc_list,
        'title':'工单系统-备件管理-添加备件记录',
        'postUrl':'/workorder/stock/new/',
        'preUrl':'/workorder/stock/log/',
        'title_content':'添加备件出入记录',
        'button_type':'add',
    }
    return render_to_response('workorder/stockNew.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockNewMore(request):
    if request.method == "POST":
        tmp_request = request.POST.copy()
        tmp_request["id_user"] = request.user.id
        form = StockInoutAddForm(tmp_request)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/stock/log/')
    #else:
    #    form = StockInoutAddForm()

    kwvars = {
        'request':request,
        'title':'工单系统-备件管理-添加备件记录',
        'postUrl':'/workorder/stock/inout/',
        'preUrl':'/workorder/stock/log/',
        'title_content':'添加备件出入记录',
        'button_type':'add',
    }
    return render_to_response('workorder/stockNewMore.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockReplace(request):
    message = ""
    if request.method == "POST":
        try:
            id_user = request.user
            id_stock_id_bad = request.POST["id_stock_bad"]
 
            id_spare_id = request.POST["id_spare"]
            id_spare = SpareList.objects.get(id_spare = int(id_spare_id))
            stock_sn = request.POST["stock_sn"]
            stock_area = request.POST["stock_area"]
            stock_st = request.POST["stock_st"]
            flag,desc = StockOb().new(stock_area = stock_area, id_spare = id_spare, stock_sn = stock_sn)
            if flag:
                message = "添加成功,继续添加吧"
                print desc
                StockList.objects.filter(id_stock = id_stock_id_bad).update(stock_st = 4)
                id_stock_new = StockList.objects.get(stock_sn = stock_sn)
                flag,desc = StockInoutOb().new(id_spare = id_spare, stio_type = "入库", id_user = id_user, id_stock = int(id_stock_new.id_stock))
                flag,desc = StockInoutOb().new(id_spare = id_spare, stio_type = "报废", id_user = id_user, id_stock = int(id_stock_id_bad))
            else:
                message = "添加失败,请检查SN号是否重复"
            
        except Exception,ex:
            print ex
            message = "添加失败"
    stock_list_bad = StockList.objects.filter(stock_st = 0)
    idc_list = IDCList.objects.filter(idc_enable = True)
    brand_list = getBrandStock( brand = "thirdpart" )
    kwvars = {
        'request':request,
        'message':message,
        'brand_list':brand_list,
        'stock_list_bad':stock_list_bad,
        'idc_list':idc_list,
        'title':'工单系统-备件管理-备件替换',
        'postUrl':'/workorder/stock/replace/',
        'preUrl':'/workorder/stock/log/',
        'title_content':'备件替换',
        'button_type':'add',
    }
    return render_to_response('workorder/stockReplace.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockEdit(request,ID):
    iStock = StockInout.objects.get(id_stinout=ID)
    logger.info("stock edit :{0}".format(ID))
    if request.method == "POST":
        tmp_request = request.POST.copy()
        tmp_request["id_user"] = request.user.id
        form = StockInoutEditForm(tmp_request,instance=iStock)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/stock/log/')
    else:
        form = StockInoutEditForm(instance=iStock)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-库存管理-编辑备件进出记录',
        'postUrl':'/workorder/stock/edit/%s/' %ID,
        'preUrl':'/workorder/stock/log/',
        'title_content':'编辑备件进出记录',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockDel(request,ID):
    StockInout.objects.filter(id_stinout = ID).delete()
    logger.info("stock del :{0}".format(ID))
    return HttpResponseRedirect('/workorder/stock/log/')




@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockCount(request):
    mList = StockList.objects.all()
    lst = SelfPaginator(request,mList, 15)
    logger.info("stock all list")
    kwvars = {
        'lPage':lst,
        'request':request,
        'title':'工单系统-备件管理-机房备件统计',
        'title_content':'机房备件统计',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('workorder/stockCount.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockGetLog(request):
    if request.method == "GET":
        try:
            pagesize = request.GET["pageSize"]
        except:
            pagesize = 25
        mList = StockInout.objects.all().order_by('-stio_create_time')
        lst = SelfPaginator(request,mList, pagesize)
        result = {}
        result["total"] = len(mList)
        result["rows"] = []
        for lid,item in enumerate(lst.object_list):
            t_result = {}
            t_result["id"] = lid+1
            t_result["stio_create_time"] = str(item.stio_create_time)
            t_result["stio_type"] = item.stio_type
            t_result["spare_en"] = item.id_spare.spare_en
            t_result["stio_num"] = item.stio_num
            try:
                t_result["reinfo_code"] = item.id_reinfo.reinfo_code
            except Exception,ex:
                t_result["reinfo_code"] = "-"
            t_result["descript"] = item.stio_descript
            t_result["id_stock"] = ', '.join([iitem.stock_sn for iitem in item.id_stock.all()])
            try:
                t_result["user"] = item.id_user.realname
            except Exception,ex:
                t_result["user"] = "Nobody"
            t_result["oper"] = 'hello'
            result["rows"].append(t_result)
    else:
        result = { "total":0, "rows": []}
    return HttpResponse(json.dumps(result,ensure_ascii = False))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockGetCount(request):
    #area_dic = {"BJ":"北京","GD":"广东","NM":"内蒙","":"-"}
    if request.method == "GET":
        try:
            pagesize = request.GET["pageSize"]
        except:
            pagesize = 25
        sql = "select id_stock,id_spare_id,stock_area,sum(case stock_st when '1' then 1 else 0 end) stock_good, sum(case when '0' then 1 else 0 end) stock_bad from workorder_stocklist group by id_spare_id,stock_area; "
        lst = StockList.objects.raw(sql)
        result = {}
        result["rows"] = []
        brand_sum = {}
        lid = 1
        for item in lst:
            t_result = {}
            t_result["id"] = lid
            t_result["stock_area"] = area_dic[item.stock_area]
            t_result["brand"] = item.id_spare.id_brand.brand_cn
            t_result["spare"] = item.id_spare.spare_en
            t_result["count_good"] = item.stock_good
            t_result["count_bad"] = item.stock_bad
            t_result["count_sum"] = item.stock_good + item.stock_bad
            if t_result["brand"] not in brand_sum:
                brand_sum[t_result["brand"]] = {}
                brand_sum[t_result["brand"]]["count_good_sum"] = 0
                brand_sum[t_result["brand"]]["count_bad_sum"] = 0
            brand_sum[t_result["brand"]]["count_good_sum"] += item.stock_good
            brand_sum[t_result["brand"]]["count_bad_sum"] += item.stock_bad
            result["rows"].append(t_result)
            lid += 1
        for item in brand_sum:
            t_result = {}
            t_result["id"] = lid
            t_result["brand"] = item
            t_result["stock_area"] = "总数"
            t_result["count_good"] = brand_sum[item]["count_good_sum"]
            t_result["count_bad"] = brand_sum[item]["count_bad_sum"]
            t_result["count_sum"] = brand_sum[item]["count_good_sum"] + brand_sum[item]["count_bad_sum"]
            result["rows"].append(t_result)
            lid += 1
        result["total"] = lid-1
    else:
        result = { "total":0, "rows": []}
    return HttpResponse(json.dumps(result,ensure_ascii = False))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def stockGetList(request):
    stock_st_dic = {0:'坏件',1:'好件',2:'其他',3:'其他',4:'其他'}
    if request.method == "GET":
        try:
            pagesize = request.GET["pageSize"]
        except:
            pagesize = 25
        mList = StockList.objects.all()
        lst = SelfPaginator(request,mList, pagesize)
        result = {}
        result["total"] = len(mList)
        result["rows"] = []
        for lid,item in enumerate(lst.object_list):
            t_result = {}
            t_result["id"] = lid+1
            t_result["stock_area"] = area_dic[item.stock_area]
            t_result["brand"] = item.id_spare.id_brand.brand_cn
            t_result["spare"] = item.id_spare.spare_cn
            t_result["stock_sn"] = item.stock_sn
            t_result["stock_st"] = stock_st_dic[item.stock_st]
            t_result["from_to"] = "{stock_from} ~ {stock_to}".format(stock_from = item.stock_from, stock_to = item.stock_to) if item.stock_from else '-'
            result["rows"].append(t_result)
    else:
        result = { "total":0, "rows": []}
    return HttpResponse(json.dumps(result,ensure_ascii = False))
