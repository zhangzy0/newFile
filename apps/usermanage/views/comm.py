#!/usr/bin/env python
#-*- coding: utf-8 -*-

from apps.usermanage.views.permission import login_required

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
import logging
logger = logging.getLogger('admin')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def Home(request):
   return render_to_response('admin/home.html',locals(),RequestContext(request))
