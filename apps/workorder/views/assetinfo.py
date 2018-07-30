#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import csv
import codecs
import datetime
import chardet
import json

import re
from io import StringIO

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required
from django.db.models.query import QuerySet

from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
from apps.workorder.models import AssetInout,AssetList, AssetModelList,AssetTypeList,SpareBrandList
from apps.workorder.models import IDCList
from apps.usermanage.models import User
from apps.workorder.forms import AssetListForm
from plugins.myclass.workorder_models import  AssetOb, AssetInoutOb
from django.db.models import Q
import logging

default_encoding = 'utf-8'  
if sys.getdefaultencoding() != default_encoding:  
    reload(sys)  
    sys.setdefaultencoding(default_encoding)  
logger = logging.getLogger('workorder')
UUID_PATTERN = re.compile(r'[0-9a-zA-Z\-]{36}')



@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetLog(request):
    id_user = request.user
    id_idcs = id_user.idc_users.all()
    id_idcs = [int(idc.id_idc) for idc in id_idcs]
    id_idcs = tuple(id_idcs)
    if len(id_idcs) == 1:
        sql_where = 'id_idc_id = %s' % (id_idcs[0])
    else:
        sql_where = 'id_idc_id in ' + str(id_idcs)
    if request.method == "POST":
        # mList = AssetInout.objects.all()
        try:
            search_keyword = request.POST.get('keywords', "").strip()  # keywords是从url中解析
            query_dic = {}
            query_dic["id_assettype__assettype_cn__icontains"] = search_keyword
            query_dic["id_assetlist__asset_sn__icontains"] = search_keyword
            query_dic["id_assetlist__id_assetbrand__brand_cn__icontains"] = search_keyword
            query_dic["id_assetmodel__assetmodel_cn__icontains"] = search_keyword
            query_dic["id_user__username__icontains"] = search_keyword
            query_dic["asio_descript__icontains"] = search_keyword
            query_dic["asio_create_time__icontains"] = search_keyword
            query_dic["id_asinout__icontains"] = search_keyword
            Q_dic = Q()
            for key in query_dic.keys():
                if query_dic[key]: Q_dic.add(Q(**{key: query_dic[key]}), Q.OR)
            if id_user.role.role_en == "sogouer" or id_user.role.role_en == "Admin":
                mList = AssetInout.objects.filter(Q_dic).order_by('-asio_create_time')
            elif id_user.role.role_en == "idcer":
                mList = AssetInout.objects.filter(Q_dic).extra(where=[sql_where]).order_by('-asio_create_time')
        except Exception,e:
            print e
    else:
        mList = AssetInout.objects.all().order_by('-asio_create_time')
    lst = SelfPaginator(request,mList, 15)
    query = AssetInout.objects.all().query
    query.group_by = ['id_user_id',]
    user_list = QuerySet(query = query, model = AssetInout)
    kwvars = {
        'lPage':lst,
        'request':request,
        'user_list':user_list,
        'title':'工单系统-备件管理-资产记录查询',
        'title_content':'资产日志查询',
        'postUrl': '/workorder/asset/log/',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('workorder/assetLog.html',kwvars,RequestContext(request))



def getBrandStock( brand = None):
    brand_list = {}
    if brand is None:
        t_brand_list = SpareBrandList.objects.filter(brand_enable=True)
    else:
        t_brand_list = SpareBrandList.objects.filter(Q(brand_en = "sureco") | Q(brand_en = "shenma"))
    for item in t_brand_list:
        id_brand = str(item.id_brand)
        brand_list[id_brand] = {}
        brand_list[id_brand]["name"] = str(item.brand_cn)
        # t_spare_list = SpareList.objects.filter(id_brand = item)
        t_asset_list = AssetModelList.objects.filter(id_assetbrand = item,assetmodel_enable=True)
        tmp_asset_list = []
        for iitem in t_asset_list:
            tmp_asset_list.append({"val":int(iitem.id_assetmodel),"txt":str(iitem.assetmodel_en)})
        brand_list[id_brand]["vals"] = tmp_asset_list
    return brand_list

@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetNew(request):
    message = ""
    if request.method == "POST":
        try:
            id_user = request.user
            id_model_id = request.POST["id_model"]
            id_assetbrand_id = request.POST["id_brand"]
            asset_sn = request.POST["asset_sn"].strip()
            asset_type = request.POST["asset_type"]
            asset_idc = request.POST["asset_idc"]
            asset_st = request.POST["asset_st"]
            asset_des = request.POST["asset_des"]
            if not id_model_id and not id_assetbrand_id and not asset_sn and not asset_type and not asset_idc and not asset_st:
                message = "关键项不许为空"
            #更新资产
            elif AssetList.objects.filter(asset_sn=asset_sn):
                if AssetList.objects.filter(Q(asset_sn=asset_sn)&Q(asset_enable=True)):
                    message = "添加失败,请检查SN号是否重复"
                else:
                    AssetList.objects.filter(asset_sn=asset_sn).update(asset_enable=True)
                    logger.info("新增资产 :{0}".format(asset_sn,))
                    message = "添加成功,继续添加吧"
                    id_assetlist = AssetList.objects.get(asset_sn=asset_sn)
                    flag, desc = AssetInoutOb().new(id_assettype_id=asset_type,
                                                    id_idc_id=asset_idc,
                                                    id_assetmodel_id=id_model_id,
                                                    id_assetbrand_id=id_assetbrand_id,
                                                    id_assetlist=id_assetlist.id_asset,
                                                    asio_type="入库",
                                                    asio_descript=asset_des,
                                                    id_user=id_user)
            #新增资产
            else:
                flag,desc = AssetOb().new(id_idc_id = asset_idc,
                                          id_model_id=id_model_id,
                                          id_assetbrand_id=id_assetbrand_id ,
                                          id_assettype_id = asset_type ,
                                          asset_sn = asset_sn ,
                                          asset_st = asset_st,
                                          asset_descript = asset_des,
                                          id_user=id_user)
                if flag:
                    logger.info("新增资产 :{0}".format(asset_sn))
                    message = "添加成功,继续添加吧"
                    id_assetlist = AssetList.objects.get(asset_sn=asset_sn)
                    flag, desc = AssetInoutOb().new(id_assettype_id=asset_type,
                                                    id_idc_id=asset_idc,
                                                    id_assetmodel_id=id_model_id,
                                                    id_assetbrand_id =id_assetbrand_id,
                                                    id_assetlist=id_assetlist.id_asset,
                                                    asio_type="入库",
                                                    asio_descript=asset_des,
                                                    id_user=id_user)
                else:
                    message = "添加失败,请检查SN号是否重复"
                print flag,desc
        except Exception,ex:
            print ex
            message = "添加失败"
    idc_list = IDCList.objects.filter(idc_enable = True)
    type_list = AssetTypeList.objects.filter(assettype_enable = True)
    brand_list = getBrandStock( )
    kwvars = {
        'request':request,
        'message':message,
        'brand_list':brand_list,
        'idc_list':idc_list,
        'type_list':type_list,
        'title':'工单系统-备件管理-添加资产记录',
        'postUrl':'/workorder/asset/new/',
        'preUrl':'/workorder/asset/list/',
        'title_content':'添加资产出入记录',
        'button_type':'add',
    }
    return render_to_response('workorder/assetNew.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetEdit(request,ID):
    iAsset = AssetList.objects.get(id_asset=ID)
    logger.info("asset edit :{0}".format(ID))
    if request.method == "POST":
        tmp_request = request.POST.copy()
        print tmp_request
        tmp_request["id_user"] = request.user.id
        form = AssetListForm(tmp_request,instance=iAsset)
        if form.is_valid():
            form.save()
            logger.info("修改资产 :{0}".format(iAsset.asset_sn))
            flag, desc = AssetInoutOb().new(id_assettype_id=tmp_request['id_assettype'],
                                            id_idc_id=tmp_request['id_idc'],
                                            id_assetmodel_id=tmp_request['id_assetmodel'],
                                            id_assetbrand_id=tmp_request['id_assetbrand'],
                                            id_assetlist=iAsset.id_asset,
                                            asio_type="修改",
                                            asio_descript=tmp_request['asset_descript'],
                                            id_user=request.user)
            print flag, desc
            return HttpResponseRedirect('/workorder/asset/list/')
    else:
        form = AssetListForm(instance=iAsset)
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-资产列表-编辑资产列表',
        'postUrl':'/workorder/asset/edit/%s/' %ID,
        'preUrl':'/workorder/asset/list/',
        'title_content':'编辑资产列表',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetDel(request,ID):
    try:
        iAsset = AssetList.objects.filter(id_asset = ID)
        iAsset.update(asset_enable = 0)
        logger.info("删除资产 :{0}".format(iAsset.asset_sn))
        iAsset = iAsset.first()
        flag, desc = AssetInoutOb().new(id_assettype_id=iAsset.id_assettype_id,
                                        id_idc_id=iAsset.id_idc_id,
                                        id_assetmodel_id=iAsset.id_assetmodel_id,
                                        id_assetbrand_id=iAsset.id_assetbrand_id,
                                        id_assetlist=iAsset.id_asset,
                                        asio_type="出库",
                                        asio_descript=iAsset.asset_descript,
                                        id_user=request.user)
        print flag, desc
    except Exception,ex:
        print ex
    return HttpResponseRedirect('/workorder/asset/list/')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetList(request):
    """
    资产汇总列表(assetcount list)

    Function:
        search: 类型、厂商、机房、型号、工单状态
        list: all or search result
        #some detele
    Author:
        liuzhen210490@sogou-inc.com
    """
    form = {}
    form['id_type_list'] = AssetTypeList.objects.filter(assettype_enable=True)
    form['id_brand_list'] = SpareBrandList.objects.filter(brand_enable=True)
    form['id_idc_list'] = IDCList.objects.filter(idc_enable = True )
    form['id_assetmodel_list'] = AssetModelList.objects.filter(assetmodel_enable = True)
    form['id_user_list'] = User.objects.filter(is_active=True)
    form['id_st_list'] = [{'id':1,'st':'好件'},{'id':2,'st':'坏件'}]
    id_user = request.user
    id_idcs = id_user.idc_users.all()
    id_idcs = [int(idc.id_idc) for idc in id_idcs]
    id_idcs = tuple(id_idcs)
    if len(id_idcs) == 1: sql_where = 'id_idc_id = %s' %(id_idcs[0])
    else: sql_where = 'id_idc_id in '+str(id_idcs)
    if request.method == "POST":
        logger.info("request_post:%s" %(str(request.POST)))
        try:
            query_dic = {}
            query_dic["id_assettype"] = request.POST["id_type"]
            query_dic["id_assetbrand"] = request.POST["id_brand"]
            query_dic["id_idc"] = request.POST["id_idc"]
            query_dic["id_assetmodel"] = request.POST["id_assetmodel"]
            query_dic["id_user"] = request.POST["id_user"]
            query_dic["asset_st"] = request.POST["id_st"]
            query_dic["asset_sn__icontains"] = request.POST["id_sn"].strip()
            query_dic["asset_enable"] = 1
            Q_dic = Q()
            for key in query_dic.keys():
                if query_dic[key]:Q_dic.add(Q(**{key:query_dic[key]}),Q.AND)
            if id_user.role.role_en == "sogouer" or id_user.role.role_en == "Admin" :
                mList = AssetList.objects.filter(Q_dic).order_by('-asset_create_time')
            elif id_user.role.role_en == "idcer":
                mList = AssetList.objects.filter(Q_dic).extra(where=[sql_where]).order_by('-asset_create_time')
        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))
    else:
        try:
            if id_user.role.role_en == "idcer":
                mList = AssetList.objects.filter(asset_enable=1).extra(where=[sql_where]).order_by('-asset_create_time')
            else:
                mList = AssetList.objects.filter(asset_enable=1).order_by('-asset_create_time')
        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))
    try:
        mList = SelfPaginator(request,mList, 20)
    except Exception,ex:
        logger.error("Exception: %s" %(str(ex)))
        mList = []
    kwvars = {
        'lPage':mList,
        'request':request,
        'form':form,
        'title':'工单系统-资产列表-资产',
        'title_content':'资产列表',
        'postUrl':'/workorder/asset/list/',
        'button_type':'add',
    }
    return render_to_response('workorder/assetList.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetCount(request):
    """
    资产统计列表(assetcount list)

    Function:
        search: 类型、厂商、机房、型号、工单状态
        list: all or search result
        #some detele
    Author:
        liuzhen210490@sogou-inc.com
    """
    form = {}
    form['id_type_list'] = AssetTypeList.objects.filter(assettype_enable=True)
    form['id_brand_list'] = SpareBrandList.objects.filter(brand_enable=True)
    form['id_idc_list'] = IDCList.objects.filter(idc_enable = True )
    form['id_assetmodel_list'] = AssetModelList.objects.filter(assetmodel_enable = True)
    form['id_st_list'] = [{'id':1,'st':'好件'},{'id':2,'st':'坏件'}]
    id_user = request.user
    id_idcs = id_user.idc_users.all()
    id_idcs = [int(idc.id_idc) for idc in id_idcs]
    id_idcs = tuple(id_idcs)
    if len(id_idcs) == 1:
        sql_where = 'id_idc_id = %s' % (id_idcs[0])
    else:
        sql_where = 'id_idc_id in ' + str(id_idcs)
    if request.method == "POST":
        logger.info("request_post:%s" %(str(request.POST)))
        try:
            id_assettype = request.POST.get("id_type", ' ')
            if not id_assettype: id_assettype = '%%'
            id_assetbrand = request.POST.get("id_brand", ' ')
            if not id_assetbrand: id_assetbrand = '%%'
            id_idc = request.POST.get("id_idc", ' ')
            if not id_idc: id_idc = '%%'
            id_assetmodel = request.POST.get("id_assetmodel", ' ')
            if not id_assetmodel: id_assetmodel = '%%'
            asset_st = request.POST.get("id_st", ' ')
            if not asset_st: asset_st = '%%'
            if id_user.role.role_en == "sogouer" or id_user.role.role_en == "Admin" :
                sql = "select id_asset,sum(case asset_st when '1' then 1 else 0 end) as asset_good,sum(case asset_st when '2' then 1 else 0 end) as asset_bad from workorder_assetlist " \
                      "where asset_enable = 1 and id_assettype_id like '{0}' and id_assetbrand_id like '{1}' and id_idc_id like '{2}' and id_assetmodel_id like '{3}' and asset_st like '{4}' " \
                      "GROUP BY id_assettype_id,id_assetmodel_id;".format(id_assettype,id_assetbrand,id_idc,id_assetmodel,asset_st)
                mListCount = AssetList.objects.raw(sql)
                sql1 = "select id_asset,sum(case asset_st when '1' then 1 else 0 end) as asset_good,sum(case asset_st when '2' then 1 else 0 end) as asset_bad from workorder_assetlist " \
                       "where asset_enable = 1 and id_assettype_id like '{0}' and id_assetbrand_id like '{1}' and id_idc_id like '{2}' and id_assetmodel_id like '{3}' and asset_st like '{4}' " \
                       "GROUP BY id_assettype_id;".format(id_assettype,id_assetbrand,id_idc,id_assetmodel,asset_st)
                mListCount1 = AssetList.objects.raw(sql1)
            elif id_user.role.role_en == "idcer":
                sql = "select id_asset,sum(case asset_st when '1' then 1 else 0 end) as asset_good,sum(case asset_st when '2' then 1 else 0 end) as asset_bad" \
                      " from workorder_assetlist where asset_enable = 1 and {0} GROUP BY id_assettype_id,id_assetmodel_id;".format(
                    sql_where)
                mListCount = AssetList.objects.raw(sql)
                sql1 = "select id_asset,sum(case asset_st when '1' then 1 else 0 end) as asset_good,sum(case asset_st when '2' then 1 else 0 end) as asset_bad " \
                       "from workorder_assetlist where asset_enable = 1 and {0} GROUP BY id_assettype_id;".format(
                    sql_where)
                mListCount1 = AssetList.objects.raw(sql1)

        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))
    else:
        try:
            if id_user.role.role_en == "idcer":
                sql = "select id_asset,sum(case asset_st when '1' then 1 else 0 end) as asset_good,sum(case asset_st when '2' then 1 else 0 end) as asset_bad" \
                      " from workorder_assetlist where asset_enable = 1 and {0} GROUP BY id_assettype_id,id_assetmodel_id;".format(sql_where)
                mListCount = AssetList.objects.raw(sql)
                sql1 = "select id_asset,sum(case asset_st when '1' then 1 else 0 end) as asset_good,sum(case asset_st when '2' then 1 else 0 end) as asset_bad " \
                       "from workorder_assetlist where asset_enable = 1 and {0} GROUP BY id_assettype_id;".format(sql_where)
                mListCount1 = AssetList.objects.raw(sql1)
            else:
                sql = "select id_asset,sum(case asset_st when '1' then 1 else 0 end) as asset_good,sum(case asset_st when '2' then 1 else 0 end) as asset_bad " \
                      "from workorder_assetlist where asset_enable = 1 GROUP BY id_assettype_id,id_assetmodel_id;"
                mListCount = AssetList.objects.raw(sql)
                sql1 = "select id_asset,sum(case asset_st when '1' then 1 else 0 end) as asset_good,sum(case asset_st when '2' then 1 else 0 end) as asset_bad " \
                       "from workorder_assetlist where asset_enable = 1 GROUP BY id_assettype_id;"
                mListCount1 = AssetList.objects.raw(sql1)
        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))

    kwvars = {
        'mListCount':mListCount,
        'mListCount1': mListCount1,
        'request':request,
        'form':form,
        'title':'工单系统-资产统计-资产',
        'title_content':'资产统计',
        'postUrl':'/workorder/asset/count/',
        'button_type':'add',
    }
    return render_to_response('workorder/assetCount.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetExport(request):
    if request.method == "GET":
        try:
            fields = [
                field for field in AssetList._meta.fields
                if field.name not in [
                    'asset_from','asset_to','asset_enable'
                ]
            ]
            filename = 'assets-{}.csv'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
            response.write(codecs.BOM_UTF8)
            assets = AssetList.objects.filter(asset_enable=True)
            writer = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)

            header = [field.verbose_name for field in fields]
            writer.writerow(header)
            for asset in assets:
                data = []
                for field in fields:
                    value = getattr(asset,field.name)
                    if field.name == 'asset_st':
                        if value == 1:
                            value = '好件'
                        else:
                            value = '坏件'
                    data.append(value)
                writer.writerow(data)
            # for asset in assets:
            #     data = [getattr(asset, field.name) for field in fields ]
            #     writer.writerow(data)
        except Exception,ex:
            print ex
        return response


@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetExportFirst(request):
    if request.method == "GET":
        try:
            fields = [
                field for field in AssetList._meta.fields
                if field.name not in [
                    'asset_from','asset_to','asset_enable'
                ]
            ]

            filename = 'assets-{}.csv'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
            response.write(codecs.BOM_UTF8)
            assets_id_default = AssetList.objects.first().id_asset if AssetList.objects.first() else None
            assets_id_default = None
            assets = AssetList.objects.filter(id_asset=assets_id_default)
            writer = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)
            header = [field.verbose_name for field in fields]
            writer.writerow(header)
            for asset in assets:
                data = []
                for field in fields:
                    value = getattr(asset,field.name)
                    if field.name == 'asset_st':
                        if value == 1:
                            value = '好件'
                        else:
                            value = '坏件'
                    data.append(value)
                writer.writerow(data)
            # for asset in assets:
            #     data = [getattr(asset, field.name) for field in fields ]
            #     writer.writerow(data)
        except Exception,ex:
            print ex
        return response



@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetImport(request):
    if request.method == "POST":
        f = request.FILES.get('file')
        det_result = chardet.detect(f.read())
        f.seek(0)  # reset file seek index
        file_data = f.read().decode(det_result['encoding']).strip(codecs.BOM_UTF8.decode())
        csv_file = StringIO(file_data)
        reader = csv.reader(csv_file)
        csv_data = [row for row in reader]
        fields = [
            field for field in AssetList._meta.fields
            if field.name not in [
                'asset_from','asset_to','asset_enable'
            ]
            ]
        header_ = csv_data[0]
        mapping_reverse = {field.verbose_name: field.name for field in fields}
        attr = [mapping_reverse.get(n, None) for n in header_]
        if None in attr:
            data = {'valid': False,
                    'msg': '必须和模板的类型一致'}
            return HttpResponse(json.dumps(data), content_type="application/json")
        created, updated, failed = [], [], []
        assets = []
        for row in csv_data[1:]:
            if set(row) == {''}:
                continue
            asset_dict = dict(zip(attr, row))
            id_ = asset_dict.pop('id_asset', 0)
            for k, v in asset_dict.items():
                if k == 'asset_st':
                    v = 1 if v == '好件' else 2
                elif k == 'id_user':
                    v = get_object_or_none(User, realname=v)
                elif k == 'id_assetbrand':
                    v = get_object_or_none(SpareBrandList, brand_cn=v)
                elif k == 'id_assetmodel':
                    v = get_object_or_none(AssetModelList, assetmodel_en=v)
                elif k == 'id_assettype':
                    v = get_object_or_none(AssetTypeList, assettype_cn=v)
                elif k == 'id_idc':
                    v = get_object_or_none(IDCList, idc_cn=v)
                elif k in ['port', 'cpu_count', 'cpu_cores','asset_num']:
                    try:
                        v = int(v)
                    except ValueError:
                        v = 0
                else:
                    continue
                asset_dict[k] = v
            asset = get_object_or_none(AssetList, id_asset=id_)
            if not asset:
                try:
                    if len(AssetList.objects.filter(asset_sn=asset_dict.get('asset_sn'))):
                        raise Exception('already exists')
                    if not asset_dict:
                        break
                    asset = AssetList.objects.create(**asset_dict)
                    logger.info("新增资产 :{0}".format(asset_dict.get('asset_sn')))
                    id_assetlist = AssetList.objects.get(asset_sn=asset_dict.get('asset_sn'))
                    flag, desc = AssetInoutOb().new(id_assettype_id=asset_dict.get('id_assettype').id_assettype,
                                                    id_idc_id=asset_dict.get('id_idc').id_idc,
                                                    id_assetmodel_id=asset_dict.get('id_assetmodel').id_assetmodel,
                                                    id_assetbrand_id=asset_dict.get('id_assetbrand').id_brand,
                                                    id_assetlist=id_assetlist.id_asset,
                                                    asio_type="入库",
                                                    asio_descript=asset_dict.get('asset_descript'),
                                                    id_user=request.user)
                    created.append(asset_dict['asset_sn'])
                    assets.append(asset)
                except Exception as e:
                    print e
                    failed.append('%s: %s' % (asset_dict['asset_sn'], str(e)))
            else:
                try:
                    for k, v in asset_dict.items():
                        if v:
                            setattr(asset, k, v)
                except Exception as e:
                    print e
                try:
                    asset.save()
                    logger.info("修改资产 :{0}".format(asset_dict.get('asset_sn')))
                    id_assetlist = AssetList.objects.get(asset_sn=asset_dict.get('asset_sn'))
                    flag, desc = AssetInoutOb().new(id_assettype_id=asset_dict.get('id_assettype').id_assettype,
                                                    id_idc_id=asset_dict.get('id_idc').id_idc,
                                                    id_assetmodel_id=asset_dict.get('id_assetmodel').id_assetmodel,
                                                    id_assetbrand_id=asset_dict.get('id_assetbrand').id_brand,
                                                    id_assetlist=id_assetlist.id_asset,
                                                    asio_type="修改",
                                                    asio_descript=asset_dict.get('asset_descript'),
                                                    id_user=request.user)
                    updated.append(asset_dict['asset_sn'])
                except Exception as e:
                    failed.append('%s: %s' % (asset_dict['asset_sn'], str(e)))

        data = {
            'created': created,
            'created_info': 'Created {}'.format(len(created)),
            'updated': updated,
            'updated_info': 'Updated {}'.format(len(updated)),
            'failed': failed,
            'failed_info': 'Failed {}'.format(len(failed)),
            'valid': True,
            'msg': 'Created: {}. Updated: {}, Error: {}'.format(
                len(created), len(updated), len(failed))
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
        # return self.render_json_response(data)

def get_object_or_none(model, **kwargs):
    try:
        obj = model.objects.get(**kwargs)
    except Exception,e:
        return None
    return obj

