#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('apps.workorder.views',
    #url(r'^$', 'user.LoginUser'),
    #url(r'^login/$', 'user.LoginUser'),
    #url(r'^logout/$', 'user.LogoutUser'),

    #test
    url(r'^test/$', 'comm.test'), #测试
    url(r'^$', 'comm.Home'),

    #dailywo
    url(r'^dailywo/list/$', 'womanage.dailywoList'),
    url(r'^dailywo/add/$', 'womanage.dailywoAdd'),
    url(r'^dailywo/edit/(?P<ID>\d+)/$', 'womanage.dailywoEdit'),
    url(r'^dailywo/view/(?P<ID>\d+)/$', 'womanage.dailywoView'),
    url(r'^dailywo/del/(?P<ID>\d+)/$', 'womanage.dailywoDel'),

    #repariwo
    url(r'^repairwo/list/$', 'womanage.repairwoList'),
    url(r'^repairwo/add/$', 'womanage.repairwoAdd'),
    url(r'^repairwo/edit/(?P<ID>\d+)/$', 'womanage.repairwoEdit'),
    url(r'^repairwo/view/(?P<ID>\d+)/$', 'womanage.repairwoView'),
    url(r'^repairwo/del/(?P<ID>\d+)/$', 'womanage.repairwoDel'),

    #idcinfo
    url(r'^idc/list/$', 'baseinfo.idcList'),
    url(r'^idc/add/$', 'baseinfo.idcAdd'),
    url(r'^idc/edit/(?P<ID>\d+)/$', 'baseinfo.idcEdit'),
    url(r'^idc/del/(?P<ID>\d+)/$', 'baseinfo.idcDel'),

    #operinfo
    url(r'^oper/list/$', 'baseinfo.operList'),
    url(r'^oper/add/$', 'baseinfo.operAdd'),
    url(r'^oper/edit/(?P<ID>\d+)/$', 'baseinfo.operEdit'),
    url(r'^oper/del/(?P<ID>\d+)/$', 'baseinfo.operDel'),

    #brandinfo
    url(r'^brand/list/$', 'baseinfo.brandList'),
    url(r'^brand/add/$', 'baseinfo.brandAdd'),
    url(r'^brand/edit/(?P<ID>\d+)/$', 'baseinfo.brandEdit'),
    url(r'^brand/del/(?P<ID>\d+)/$', 'baseinfo.brandDel'),

    #spareinfo
    url(r'^spare/list/$', 'baseinfo.spareList'),
    url(r'^spare/add/$', 'baseinfo.spareAdd'),
    url(r'^spare/edit/(?P<ID>\d+)/$', 'baseinfo.spareEdit'),
    url(r'^spare/del/(?P<ID>\d+)/$', 'baseinfo.spareDel'),

    #modelinfo
    url(r'^model/list/$', 'baseinfo.modelList'),
    url(r'^model/add/$', 'baseinfo.modelAdd'),
    url(r'^model/edit/(?P<ID>\d+)/$', 'baseinfo.modelEdit'),
    url(r'^model/del/(?P<ID>\d+)/$', 'baseinfo.modelDel'),

    #wostatusinfo
    url(r'^status/list/$', 'baseinfo.statuslList'),
    url(r'^status/add/$', 'baseinfo.statusAdd'),
    url(r'^status/edit/(?P<ID>\d+)/$', 'baseinfo.statusEdit'),
    url(r'^status/del/(?P<ID>\d+)/$', 'baseinfo.statusDel'),

   #engineerinfo
    url(r'^engineer/list/$','baseinfo.engineerList'),
    url(r'^engineer/add/$', 'baseinfo.engineerAdd'),
    url(r'^engineer/edit/(?P<ID>\d+)/$', 'baseinfo.engineerEdit'),
    url(r'^engineer/del/(?P<ID>\d+)/$', 'baseinfo.engineerDel'),

    url(r'^assetmodel/list/$','baseinfo.assetModelList'),
    url(r'^assetmodel/add/$', 'baseinfo.assetModelAdd'),
    url(r'^assetmodel/edit/(?P<ID>\d+)/$', 'baseinfo.assetModelEdit'),
    url(r'^assetmodel/del/(?P<ID>\d+)/$', 'baseinfo.assetModelDel'),

    #faultinfo
    url(r'^fault/list/$', 'baseinfo.faultList'),
    url(r'^fault/add/$', 'baseinfo.faultAdd'),
    url(r'^fault/edit/(?P<ID>\d+)/$', 'baseinfo.faultEdit'),
    url(r'^fault/del/(?P<ID>\d+)/$', 'baseinfo.faultDel'),

    #stockinfo
    url(r'^stock/new/$', 'stockinfo.stockNew'),
    url(r'^stock/newmore/$', 'stockinfo.stockNewMore'),
    url(r'^stock/replace/$', 'stockinfo.stockReplace'),
    url(r'^stock/log/$', 'stockinfo.stockLog'),
    url(r'^stock/count/$', 'stockinfo.stockCount'),
    url(r'^stock/del/(?P<ID>\d+)/$', 'stockinfo.stockDel'),
    url(r'^stock/edit/(?P<ID>\d+)/$', 'stockinfo.stockEdit'),

    # stock get data
    url(r'^stock/api_getlog/$', 'stockdata.stockGetLog'),
    url(r'^stock/api_getlist/$', 'stockdata.stockGetList'),
    url(r'^stock/api_getcount/$', 'stockdata.stockGetCount'),
    url(r'^repairwo/getnewspare/$', 'stockdata.dataGetnewspare'),

    # stock api actions
    url(r'^stock/api_del_stocklogs/$', 'stockaction.apiDelStocklogs'),

    # assetinfo
    url(r'^asset/list/$', 'assetinfo.assetList'),
    url(r'^asset/count/$', 'assetinfo.assetCount'),
    url(r'^asset/new/$', 'assetinfo.assetNew'),
    url(r'^asset/log/$', 'assetinfo.assetLog'),
    url(r'^asset/del/(?P<ID>\d+)/$', 'assetinfo.assetDel'),
    url(r'^asset/edit/(?P<ID>\d+)/$', 'assetinfo.assetEdit'),
    url(r'^asset/export/$', 'assetinfo.assetExport'),
    url(r'^asset/export/first/$', 'assetinfo.assetExportFirst'),
    url(r'^asset/import/$', 'assetinfo.assetImport'),


    #url(r'^stock/api_getlist/$', 'stockinfo.stockGetList'),

    # #commute
    url(r'^commute/doit/$', 'commuteinfo.commuteDoit'),
    url(r'^commute/list/$', 'commuteinfo.commuteList'),
    url(r'^commute/count/$', 'commuteinfo.commuteCount'),
    url(r'^commute/explain/list/$', 'commuteinfo.explainList'),
    url(r'^commute/explain/record/list/$', 'commuteinfo.explainRecordList'),

    # commute get data 
    url(r'^commute/api_get_commute/$', 'commuteapi.getCommute'),
    url(r'^commute/api_get_commute_explain_list/$', 'commuteapi.getCommuteExplainList'),
    url(r'^commute/api_add_comm_explain/$', 'commuteapi.addCommExplain'),
    url(r'^commute/api_add_comm_explain_form/$', 'commuteapi.addCommExplainForm'),
    url(r'^commute/api_del_comm_attach/$', 'commuteapi.delCommExplainFile'),
    #url(r'^commute/api_add_comm_explain_file/$', 'commuteapi.addCommExplainFile'),


    # overtime
    url(r'^overtime/list/$', 'commuteinfo.overtimeList'), #所有加班记录
    url(r'^overtime/add/$', 'commuteinfo.overtimeAdd'),   #添加加班申请
    url(r'^overtime/del/(?P<ID>\d+)/$', 'commuteinfo.overtimeDel'), #所有加班记录
    url(r'^overtime/edit/(?P<ID>\d+)/$', 'commuteinfo.overtimeEdit'), #被打回或未提交时可编辑
    url(r'^overtime/view/(?P<ID>\d+)/$', 'commuteinfo.overtimeView'), #加班申请详情

    # overtime record
    url(r'^overtime/record/list/$', 'commuteinfo.overtimeRecordList'), #待审批及所有审批单(tab)
    url(r'^overtime/record/view/(?P<ID>\d+)/$', 'commuteinfo.overtimeRecordView'), #加班申请详情

    #access acl
    url(r'^access/acl/$', 'accessinfo.aclList'),
    url(r'^access/acl/add/$', 'accessinfo.aclAdd'),
    url(r'^access/acl/edit/(?P<ID>\d+)/$', 'accessinfo.aclEdit'),
    url(r'^access/acl/del/(?P<ID>\d+)/$', 'accessinfo.aclDel'),

    #usermanage
    url(r'^user/settings/$', 'userinfo.userinfoView'), #用户基本信息展示
    url(r'^user/settings/edit/$', 'userinfo.userinfoEdit'), #编辑模式
    url(r'^user/changepwd/$', 'userinfo.changepwd'), #编辑模式

)
