#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.shelves.views',
    url(r'^$', 'comm.shelvesHome'), #index
    url(r'help/$', 'comm.shelvesHelp'), #help
    url(r'checkok/$', 'comm.shelvesCheckOK'), #checkok
    url(r'checkcount/$', 'comm2.shelvesCheckCount'), #checkcount
    url(r'api_get_faults/$', 'apis.getFaults'), #get faults
    url(r'api_add_faults/$', 'apis.addFaults'), #add faults
    url(r'api_power_on/$', 'apis.powerOn'), #Power on auth
)
