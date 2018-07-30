#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
rocshow URL
"""
from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.rocshow.views',
    url(r'^$', 'comm.dashboard'),
    url(r'^faultdetail/$', 'comm.faultDetail'),
    url(r'^faultcount/$', 'comm.faultCount'),
    url(r'^faultsearch/$', 'comm.faultSearch'),
    url(r'^error404/$', 'comm.error404'),
    url(r'^error500/$', 'comm.error500'),
)
