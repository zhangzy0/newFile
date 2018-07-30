#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from website.common.CommonPaginator import SelfPaginator

from apps.usermanage.forms import PermissionListForm
from apps.usermanage.models import User,RoleList,PermissionList
from apps.workorder.models import Acl
from plugins.codegit.ipy_net import isSubNet,clientIP
import re
import logging
logger = logging.getLogger('admin')


def IpaddressAcl():
    '''限制IP登录
    '''
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            ipaddress = clientIP(request)
            Flag = False
            for item in Acl.objects.all():
                if isSubNet(ipaddress,item.acl_ip,item.acl_mask):
                    Flag = True
                    break
            if not Flag:
                return HttpResponseRedirect('/accounts/login/')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
    

def PermissionVerify():
    '''权限认证模块,
        此模块会先判断用户是否是管理员（is_superuser为True），如果是管理员，则具有所有权限,
        如果不是管理员则获取request.user和request.path两个参数，判断两个参数是否匹配，匹配则有权限，反之则没有。
    '''
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            #iUser = User.objects.get(username=request.user)
            iUser = User.objects.get(realname=request.user)

            if not iUser.is_superuser: #判断用户如果是超级管理员则具有所有权限
                if not iUser.role: #如果用户无角色，直接返回无权限
                    return HttpResponseRedirect('/accounts/permission/deny')

                role_permission = RoleList.objects.get(id_role=iUser.role.id_role)
                role_permission_list = role_permission.id_perm.all()

                matchUrl = []
                current_url = re.split(r'(\d)',request.path)[0]
                for item in role_permission_list:
                    if current_url == item.per_url or request.path.rstrip('/') == item.per_url:
                        matchUrl.append(item.per_url)
                print '%s---->matchUrl:%s' %(request.user,str(matchUrl))
                if len(matchUrl) == 0:
                    return HttpResponseRedirect('/accounts/permission/deny')
            else:
                pass

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    return decorator

def login_required():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return HttpResponseRedirect('/accounts/login/')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
    

#@login_required()
def NoPermission(request):

    kwvars = {
        'request':request,
    }

    return render_to_response('admin/usermanage/nopermission.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def AddPermission(request):
    if request.method == "POST":
        form = PermissionListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/permission/list')
    else:
        form = PermissionListForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'Permission Add',
        'postUrl':'/accounts/permission/add/',
    }

    return render_to_response('admin/common/formadd.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def ListPermission(request):
    mList = PermissionList.objects.all()
    for item in mList:
        try:
            tItem = PermissionList.objects.get(id_perm = item.per_pid)
            item.per_pid = "%s(%s)" %(tItem.per_cn,tItem.per_url)
            #item.per_pid = tItem["per_cn"]
        except:
            item.per_pid = "------"
    #分页功能
    lst = SelfPaginator(request,mList, 30)
    kwvars = {
        'lPage':lst,
        'request':request,
    }
    return render_to_response('admin/usermanage/permissionlist.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def EditPermission(request,ID):
    iPermission = PermissionList.objects.get(id_perm = ID)
    if request.method == "POST":
        form = PermissionListForm(request.POST,instance= iPermission)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/permission/list')
    else:
        form = PermissionListForm(instance=iPermission)

    kwvars = {
        'form':form,
        'request':request,
        'title':'Permission Edit',
        'postUrl':'/accounts/permission/edit/%s/' %ID,
    }

    return render_to_response('admin/common/formedit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def DeletePermission(request,ID):
    PermissionList.objects.filter(id_perm = ID).delete()

    return HttpResponseRedirect('/accounts/permission/list')
