#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required

from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
from apps.usermanage.models import User
from apps.workorder.models import Acl
from apps.workorder.forms import AclForm
import logging
logger = logging.getLogger('workorder')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def aclList(request):
    form = {}
    mList = Acl.objects.all()
    #lst = SelfPaginator(request,mList, 15)
    #print len(mList)
    kwvars = {
        'form':form,
        'lPage':mList,
        'request':request,
        'title':'工单系统-访问控制',
        'title_content':'访问控制白名单',
    }
    return render_to_response('workorder/aclList.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def aclEdit(request,ID):
    iAcl = Acl.objects.get(id_acl=ID)
    if request.method == "POST":
        tmp_request = request.POST.copy()
        tmp_request["id_user"] = request.user.id
        form = AclForm(tmp_request,instance=iAcl)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/access/acl/')
    else:
        form = AclForm(instance=iAcl)
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-加班申请-编辑加班申请',
        'title_content':'编辑加班申请',
        'postUrl':'/workorder/access/acl/edit/%s/' %ID,
        'preUrl':'/workorder/access/acl/',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def aclAdd(request):
    if request.method == "POST":
        tmp_request = request.POST.copy()
        tmp_request["id_user"] = request.user.id
        form = AclForm(tmp_request)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workorder/access/acl/')
    else:
        form = AclForm()
        
    kwvars = {
        'form':form,
        'request':request,
        'button_type':'add',
        'title':'工单系统-访问控制-新增规则',
        'title_content':'新增规则',
        'postUrl':'/workorder/access/acl/add/',
        'preUrl':'/workorder/access/acl/',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def aclDel(request,ID):
    Acl.objects.filter(id_acl = ID).delete()
    return HttpResponseRedirect('/workorder/access/acl/')
