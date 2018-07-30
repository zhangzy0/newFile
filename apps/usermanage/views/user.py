#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required

from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl

from django.contrib import auth
from django.contrib.auth import get_user_model
from apps.usermanage.forms import LoginUserForm,ChangePasswordForm,AddUserForm,EditUserForm
from plugins.codegit.ipy_net import isSubNet,clientIP
from apps.workorder.models import Acl
import logging
logger = logging.getLogger('admin')

def LoginUser(request):
    '''用户登录view'''
    ipaddress = clientIP(request)
    try:
        appname = request.path.split('/')[0]
        if appname != "shelves":
            Flag = False
            ipdenyinfo = ""
            for item in Acl.objects.all():
                if isSubNet(ipaddress,item.acl_ip,item.acl_mask):
                    Flag = True
                    break
            if not Flag:
                ipdenyinfo = ipaddress
    except Exception,ex:
        print ex

    if request.user.is_authenticated() and Flag:
        return HttpResponseRedirect('/')

    print request.GET
    print request.POST
    if request.method == 'GET' and request.GET.has_key('next'):
        next = request.GET['next']
    elif request.method == 'GET' and request.GET.has_key('service'):
        next = request.GET['service']
    else:
        next = '/'


    if request.method == "POST":
        form = LoginUserForm(request, data=request.POST)
        print 'post'
        if form.is_valid() and Flag:
            print 'ok'
            auth.login(request, form.get_user())
            return HttpResponseRedirect(request.POST['next'])
    else:
        form = LoginUserForm(request)

    kwvars = {
        'request':request,
        'form':form,
        'next':next,
        'ipdenyinfo':ipdenyinfo,
    }

    #return render_to_response('admin/usermanage/login2.html',kwvars,RequestContext(request))
    return render_to_response('admin/usermanage/login.html',kwvars,RequestContext(request))


@login_required()
def LogoutUser(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def ChangePassword(request):
    if request.method=='POST':
        form = ChangePasswordForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/logout/')
    else:
        form = ChangePasswordForm(user=request.user)

    kwvars = {
        'form':form,
        'request':request,
    }

    return render_to_response('admin/usermanage/changepwd.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def ListUser(request):
    mList = get_user_model().objects.all()

    #分页功能
    lst = SelfPaginator(request,mList, 30)

    kwvars = {
        'lPage':lst,
        'request':request,
    }

    return render_to_response('admin/usermanage/userlist.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def AddUser(request):

    if request.method=='POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            form.save()
            return HttpResponseRedirect('/accounts/user/list')
    else:
        form = AddUserForm()

    kwvars = {
        'form':form,
        'request':request,
        'title':'User Add',
        'postUrl':'/accounts/user/add/',
    }

    return render_to_response('admin/usermanage/useradd.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def DeleteUser(request,ID):
    if ID == '1':
        return HttpResponse(u'超级管理员不允许删除!!!')
    else:
        get_user_model().objects.filter(id = ID).delete()

    return HttpResponseRedirect('/accounts/user/list')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def EditUser(request,ID):
    user = get_user_model().objects.get(id = ID)

    if request.method=='POST':
        form = EditUserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/user/list')
    else:
        form = EditUserForm(instance=user
        )

    kwvars = {
        'form':form,
        'object':user,
        'request':request,
        'title':'User Edit',
        'postUrl':'/accounts/user/edit/%s/' %ID,
    }

    return render_to_response('admin/usermanage/useredit.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def ResetPassword(request,ID):
    user = get_user_model().objects.get(id = ID)

    newpassword = get_user_model().objects.make_random_password(length=10,allowed_chars='abcdefghjklmnpqrstuvwxyABCDEFGHJKLMNPQRSTUVWXY3456789')
    print '====>ResetPassword:%s-->%s' %(user.username,newpassword)
    user.set_password(newpassword)
    user.save()

    kwvars = {
        'object':user,
        'newpassword':newpassword,
        'request':request,
    }

    return render_to_response('admin/usermanage/resetpwd.html',kwvars,RequestContext(request))
