#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required

from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
from apps.usermanage.forms import RoleListForm
from apps.usermanage.models import RoleList
import logging
logger = logging.getLogger('admin')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def AddRole(request):
    if request.method == "POST":
        form = RoleListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/role/list')
    else:
        form = RoleListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'Role Add',
        'postUrl':'/accounts/role/add/',
    }

    return render_to_response('admin/usermanage/roleadd.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def ListRole(request):
    mList = RoleList.objects.all()

    #分页功能
    lst = SelfPaginator(request,mList, 30)

    kwvars = {
        'lPage':lst,
        'request':request,
    }

    return render_to_response('admin/usermanage/rolelist.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def EditRole(request,ID):
    iRole = RoleList.objects.get(id_role=ID)

    if request.method == "POST":
        form = RoleListForm(request.POST,instance=iRole)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/role/list')
    else:
        form = RoleListForm(instance=iRole)

    kwvars = {
        'form':form,
        'request':request,
        'title':'Role Edit',
        'postUrl':'/accounts/role/edit/%s/' %ID,
    }

    return render_to_response('admin/usermanage/roleedit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def DeleteRole(request,ID):
    RoleList.objects.filter(id_role = ID).delete()

    return HttpResponseRedirect('/accounts/role/list')
