#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
apis 接口的URL
"""
from django.conf.urls import patterns, include, url
from apps.apis.views.usermanage import *
#from rest_framework import router


urlpatterns = patterns('apps.apis.views',
    #url(r'^', include(router.urls)),
    url(r'^order/$', 'workorder.dailywo'),
    url(r'^repair/$', 'workorder.repairwo'),
    #url(r'^api/login$', LoginViewSet.as_view()),
)
