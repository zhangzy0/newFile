#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required

from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
from apps.workorder.models import IDCList,OperList,SpareBrandList,SpareList,ModelList,StatusList,FaultList,EngineerList,AssetModelList
from apps.usermanage.models import User
from apps.workorder.forms import IDCListForm,OperListForm,SpareBrandListForm,SpareListForm,ModelListForm,StatusListForm,FaultListForm,EngineerListForm,AssetModelListForm
import logging
logger = logging.getLogger('workorder')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def idcList(request):
    mList = IDCList.objects.all()
    #mList = IDCList.objects.raw('select * from usermanage_user right join workorder_idclist on workorder_idclist.id_idc = usermanage_user.id_idc;') 
    #分页功能
    lst = SelfPaginator(request,mList, 15)
    #lst = SelfPaginator(request,list(mList), 15)
    kwvars = {
        'lPage':lst,
        'request':request,
        'title':'工单系统-基础信息-机房信息列表',
        #'postUrl':'/workorder/idc/list/',
    }
    return render_to_response('workorder/idcList.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def idcAdd(request):
    if request.method == "POST":
        form = IDCListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/idc/list')
    else:
        form = IDCListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加机房信息',
        'postUrl':'/workorder/idc/add/',
        'preUrl':'/workorder/idc/list/',
        'title_content':'添加机房信息',
        'button_type':'add',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def idcEdit(request,ID):
    iIDC = IDCList.objects.get(id_idc=ID)
    if request.method == "POST":
        form = IDCListForm(request.POST,instance=iIDC)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/idc/list')
    else:
        form = IDCListForm(instance=iIDC)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑机房信息',
        'postUrl':'/workorder/idc/edit/%s/' %ID,
        'preUrl':'/workorder/idc/list/',
        'title_content':'编辑机房信息',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def idcDel(request,ID):
    IDCList.objects.filter(id_idc = ID).delete()
    return HttpResponseRedirect('/workorder/idc/list')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def operList(request):
    mList = OperList.objects.all()
    for item in mList:
        try:
            tItem = OperList.objects.get(id_op = item.op_pid)
            item.op_pid = tItem.op_cn
        except:
            item.op_pid = "------"
    lst = SelfPaginator(request,mList, 15)
    kwvars = {
        'lPage':lst,
        'request':request,
        'title':'工单系统-基础信息-操作类型列表',
        #'postUrl':'/workorder/oper/list/',
    }

    return render_to_response('workorder/operList.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def operAdd(request):
    if request.method == "POST":
        form = OperListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/oper/list')
    else:
        form = OperListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加操作类型',
        'postUrl':'/workorder/oper/add/',
        'preUrl':'/workorder/oper/list/',
        'title_content':'添加操作类型',
        'button_type':'add',
    }

    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def operEdit(request,ID):
    iOper = OperList.objects.get(id_op=ID)

    if request.method == "POST":
        form = OperListForm(request.POST,instance=iOper)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/oper/list')
    else:
        form = OperListForm(instance=iOper)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑操作类型',
        'postUrl':'/workorder/oper/edit/%s/' %ID,
        'preUrl':'/workorder/oper/list/',
        'title_content':'编辑操作类型',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def operDel(request,ID):
    OperList.objects.filter(id_op = ID).delete()
    return HttpResponseRedirect('/workorder/oper/list')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def brandList(request):
    mList = SpareBrandList.objects.all()
    #分页功能
    lst = SelfPaginator(request,mList, 15)
    kwvars = {
        'lPage':lst,
        'request':request,
        'title':'工单系统-基础信息-厂商列表',
    }
    return render_to_response('workorder/brandList.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def brandAdd(request):
    if request.method == "POST":
        form = SpareBrandListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/brand/list')
    else:
        form = SpareBrandListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加厂商信息',
        'postUrl':'/workorder/brand/add/',
        'preUrl':'/workorder/brand/list/',
        'title_content':'添加厂商信息',
        'button_type':'add',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))
    
@login_required()
@IpaddressAcl()
@PermissionVerify()
def brandEdit(request,ID):
    iBrand = SpareBrandList.objects.get(id_brand=ID)
    if request.method == "POST":
        form = SpareBrandListForm(request.POST,instance=iBrand)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/brand/list')
    else:
        form = SpareBrandListForm(instance=iBrand)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑厂商信息',
        'postUrl':'/workorder/brand/edit/%s/' %ID,
        'preUrl':'/workorder/brand/list/',
        'title_content':'编辑厂商信息',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def brandDel(request,ID):
    SpareBrandList.objects.filter(id_brand = ID).delete()
    return HttpResponseRedirect('/workorder/brand/list')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def spareList(request):
    mList = SpareList.objects.all()
    #分页功能
    lst = SelfPaginator(request,mList, 15)
    kwvars = {
        'lPage':lst,
        'request':request,
        'title':'工单系统-基础信息-备件型号列表',
    }
    return render_to_response('workorder/spareList.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def spareAdd(request):
    if request.method == "POST":
        form = SpareListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/spare/list')
    else:
        form = SpareListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加备件类型信息',
        'postUrl':'/workorder/spare/add/',
        'preUrl':'/workorder/spare/list/',
        'title_content':'添加备件类型',
        'button_type':'add',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def spareEdit(request,ID):
    iSpare = SpareList.objects.get(id_spare=ID)
    if request.method == "POST":
        form = SpareListForm(request.POST,instance=iSpare)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/spare/list')
    else:
        form = SpareListForm(instance=iSpare)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑备件信息',
        'postUrl':'/workorder/spare/edit/%s/' %ID,
        'preUrl':'/workorder/spare/list/',
        'title_content':'编辑备件类型',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def spareDel(request,ID):
    SpareList.objects.filter(id_spare = ID).delete()
    return HttpResponseRedirect('/workorder/spare/list')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def engineerList(request):
    mList = EngineerList.objects.all()
    lst = SelfPaginator(request,mList,15)
    kwvars = {
        'lPage': lst,
        'request': request,
        'title': '工单系统-基础信息-厂商工程师列表',
    }
    return render_to_response('workorder/engineerList.html', kwvars, RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def engineerAdd(request):
    if request.method == "POST":
        form = EngineerListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/engineer/list')
    else:
        form = EngineerListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加工程师信息',
        'postUrl':'/workorder/engineer/add/',
        'preUrl':'/workorder/engineer/list/',
        'title_content':'添加工程师信息',
        'button_type':'add',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def engineerEdit(request,ID):
    iModel = EngineerList.objects.get(id_engineer=ID)
    if request.method == "POST":
        form = EngineerListForm(request.POST,instance=iModel)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/engineer/list')
    else:
        form = EngineerListForm(instance=iModel)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑工程师信息',
        'postUrl':'/workorder/engineer/edit/%s/' %ID,
        'preUrl':'/workorder/engineer/list/',
        'title_content':'编辑工程师信息',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def engineerDel(request,ID):
    EngineerList.objects.filter(id_engineer = ID).delete()
    return HttpResponseRedirect('/workorder/engineer/list')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetModelList(request):
    mList = AssetModelList.objects.all()
    lst = SelfPaginator(request,mList,15)
    kwvars = {
        'lPage': lst,
        'request': request,
        'title': '工单系统-基础信息-资产型号列表',
    }
    return render_to_response('workorder/assetModelList.html', kwvars, RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetModelAdd(request):
    if request.method == "POST":
        form = AssetModelListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/assetmodel/list')
    else:
        form = AssetModelListForm()
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加资产类型信息',
        'postUrl':'/workorder/assetmodel/add/',
        'preUrl':'/workorder/assetmodel/list/',
        'title_content':'添加资产类型信息',
        'button_type':'add',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetModelEdit(request,ID):
    iModel = AssetModelList.objects.get(id_assetmodel=ID)
    if request.method == "POST":
        form = AssetModelListForm(request.POST,instance=iModel)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/assetmodel/list')
    else:
        form = AssetModelListForm(instance=iModel)
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑资产型号信息',
        'postUrl':'/workorder/assetmodel/edit/%s/' %ID,
        'preUrl':'/workorder/assetmodel/list/',
        'title_content':'编辑资产型号信息',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def assetModelDel(request,ID):
    AssetModelList.objects.filter(id_assetmodel = ID).delete()
    return HttpResponseRedirect('/workorder/assetmodel/list')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def modelList(request):
    mList = ModelList.objects.all()
    lst = SelfPaginator(request,mList, 15)
    kwvars = {
        'lPage':lst,
        'request':request,
        'title':'工单系统-基础信息-机型列表',
    }
    return render_to_response('workorder/modelList.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def modelAdd(request):
    if request.method == "POST":
        form = ModelListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/model/list')
    else:
        form = ModelListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加机型信息',
        'postUrl':'/workorder/model/add/',
        'preUrl':'/workorder/model/list/',
        'title_content':'添加机型信息',
        'button_type':'add',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def modelEdit(request,ID):
    iModel = ModelList.objects.get(id_model=ID)
    if request.method == "POST":
        form = ModelListForm(request.POST,instance=iModel)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/model/list')
    else:
        form = ModelListForm(instance=iModel)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑机型信息',
        'postUrl':'/workorder/model/edit/%s/' %ID,
        'preUrl':'/workorder/model/list/',
        'title_content':'编辑机型信息',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def modelDel(request,ID):
    ModelList.objects.filter(id_model = ID).delete()
    return HttpResponseRedirect('/workorder/model/list')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def statuslList(request):
    mList = StatusList.objects.all()
    lst = SelfPaginator(request,mList, 15)
    kwvars = {
        'lPage':lst,
        'request':request,
        'title':'工单系统-基础信息-工单状态类型',
    }
    return render_to_response('workorder/statusList.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def statusAdd(request):
    if request.method == "POST":
        form = StatusListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/status/list')
    else:
        form = StatusListForm()
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加工单状态信息',
        'postUrl':'/workorder/status/add/',
        'preUrl':'/workorder/status/list/',
        'title_content':'添加工单状态信息',
        'button_type':'add',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def statusEdit(request,ID):
    iStatus = StatusList.objects.get(id_st=ID)
    if request.method == "POST":
        form = StatusListForm(request.POST,instance=iStatus)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/status/list')
    else:
        form = StatusListForm(instance=iStatus)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑工单状态信息',
        'postUrl':'/workorder/status/edit/%s/' %ID,
        'preUrl':'/workorder/status/list/',
        'title_content':'编辑工单状态信息',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def statusDel(request,ID):
    StatusList.objects.filter(id_st = ID).delete()
    return HttpResponseRedirect('/workorder/status/list')



@login_required()
@IpaddressAcl()
@PermissionVerify()
def faultList(request):
    mList = FaultList.objects.all()
    lst = SelfPaginator(request,mList, 15)
    kwvars = {
        'lPage':lst,
        'request':request,
        'title':'工单系统-基础信息-故障类型',
    }
    return render_to_response('workorder/faultList.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def faultAdd(request):
    if request.method == "POST":
        form = FaultListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/fault/list')
    else:
        form = FaultListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-添加故障类型',
        'postUrl':'/workorder/fault/add/',
        'preUrl':'/workorder/fault/list/',
        'title_content':'添加故障类型',
        'button_type':'add',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def faultEdit(request,ID):
    iFault = FaultList.objects.get(id_fault=ID)
    if request.method == "POST":
        form = FaultListForm(request.POST,instance=iFault)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/fault/list')
    else:
        form = FaultListForm(instance=iFault)

    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-基础信息-编辑故障类型',
        'postUrl':'/workorder/fault/edit/%s/' %ID,
        'preUrl':'/workorder/fault/list/',
        'title_content':'编辑故障类型',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))




@login_required()
@IpaddressAcl()
@PermissionVerify()
def faultDel(request,ID):
    FaultList.objects.filter(id_fault = ID).delete()
    return HttpResponseRedirect('/workorder/fault/list')
