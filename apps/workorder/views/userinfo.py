#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required

from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
from apps.usermanage.models import User
from apps.usermanage.forms import ChangePasswordForm
from apps.workorder.models import Acl
from apps.workorder.forms import AclForm
import logging
logger = logging.getLogger('workorder')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def changepwd(request):
    message = ""
    if request.method=='POST':
        form = ChangePasswordForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            message = "修改成功"
            return HttpResponseRedirect('/accounts/logout/')
    else:
        form = ChangePasswordForm(user=request.user)

    kwvars = {
        'form':form,
        'request':request,
        'message':message,
        'title':'工单系统-用户设置-修改密码',
        'postUrl':'/workorder/user/changepwd/',
        'preUrl':'/workorder/user/changepwd/',
        'title_content':'修改密码',
        'button_type':'update',
    }
    return render_to_response('workorder/common/formAddEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def userinfoEdit(request):
    return render_to_response('workorder/userinfoEdit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def userinfoView(request):
    kwvars = {
        'request':request,
        'title':'工单系统-用户配置-用户详情',
        'title_content':'用户详情',
    }
    return render_to_response('workorder/userinfoView.html',kwvars,RequestContext(request))
