#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required

from django.db.models import F
from django.db.models import Q

import datetime
import time
import os
import logging
import re
import urllib
import json

from apps.usermanage.views.permission import PermissionVerify,IpaddressAcl
from apps.usermanage.models import User
from apps.workorder.models import StatusList,OperList,IDCList,ModelList,EngineerList
from apps.workorder.models import ModelList,FaultList,SpareList,FaultTypeList
from apps.workorder.models import DailyInfo,RepairInfo,DailywoAttach,Remark
from apps.workorder.models import Process,RepairInfoFault,SpareLack
from apps.workorder.models import DailyInfoFault
from apps.workorder.forms import DailyInfoEditForm

from plugins.codegit.urls_workorder import urllib_get
from plugins.codegit.sms import send_sms
from plugins.codegit.qq import SmartQQ
from plugins.codegit.file_oper import file_upload 
from plugins.myclass.workorder_models import RepairInfoFaultOb, RepairInfoOb
from plugins.myclass.workorder_models import DailyInfoOb, DailywoAttachOb
from plugins.myclass.workorder_models import ProcessOb, RemarkOb, DailyInfoFaultOb,SpareLackOb
from website.common.CommonPaginator import SelfPaginator

logger = logging.getLogger('workorder')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def dataGetdailywo(request):
    if request.method == "GET":
        try:
            pagesize = request.GET["pagesize"]
        except Exception,ex:
            pagesize = 25
    #stock_st_dic = {0:'坏件',1:'好件',2:'其他',3:'其他',4:'其他'}
    #if request.method == "GET":
    #    try:
    #        pagesize = request.GET["pageSize"]
    #    except:
    #        pagesize = 25
    #    mList = StockList.objects.all()
    #    lst = SelfPaginator(request,mList, pagesize)
    #    result = {}
    #    result["total"] = len(mList)
    #    result["rows"] = []
    #    for lid,item in enumerate(lst.object_list):
    #        t_result = {}
    #        t_result["id"] = lid+1
    #        t_result["stock_area"] = area_dic[item.stock_area]
    #        t_result["brand"] = item.id_spare.id_brand.brand_cn
    #        t_result["spare"] = item.id_spare.spare_cn
    #        t_result["stock_sn"] = item.stock_sn
    #        t_result["stock_st"] = stock_st_dic[item.stock_st]
    #        result["rows"].append(t_result)
    #else:
    #    result = { "total":0, "rows": []}
    #return HttpResponse(json.dumps(result,ensure_ascii = False))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def dailywoList(request):
    """
    日常工单列表(dailywo list)

    Function:
        search: 工单号、机房、创建人、工单内容、工单状态
        list: all or search result
        #some detele
    Author:
        liuzhen210490@sogou-inc.com
    """

    form = {}
    form['id_idc_list'] = IDCList.objects.filter(idc_enable = True )
    form['id_st_list'] = StatusList.objects.filter(st_enable = True)
    form['id_user_list'] = User.objects.filter(is_active = True)
    id_user = request.user
    id_idcs = id_user.idc_users.all()
    id_idcs = [int(idc.id_idc) for idc in id_idcs]
    id_idcs = tuple(id_idcs)
    if len(id_idcs) == 1: sql_where = 'id_idc_id = %s' %(id_idcs[0])
    else: sql_where = 'id_idc_id in '+str(id_idcs)
    if request.method == "POST":
        print 'hello'
        logger.info("request_post:%s" %(str(request.POST)))
        try:
            # search
            query_dic = {}
            query_dic["dainfo_code__contains"] = request.POST["dainfo_code"]
            query_dic["id_idc"] = request.POST["id_idc"]
            query_dic["id_user"] = request.POST["id_user"]
            query_dic["dainfo_content__contains"] = request.POST["dainfo_content"]
            query_dic["id_st"] = request.POST["id_st"]
            Q_dic = Q()
            for key in query_dic.keys():
                if query_dic[key]:Q_dic.add(Q(**{key:query_dic[key]}),Q.AND)
            if id_user.role.role_en == "sogouer" or id_user.role.role_en == "Admin" or id_user.role.role_en == "daily_wo":
                print 1122,Q_dic
                mList = DailyInfo.objects.filter(Q_dic).order_by('-dainfo_create_time')
            elif id_user.role.role_en == "idcer":
                print 2233,Q_dic
                mList = DailyInfo.objects.filter(Q_dic).extra(where=[sql_where]).order_by('-dainfo_create_time')
            
        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))
            #mList = DailyInfo.objects.filter(Q_dic).order_by('-dainfo_create_time')
    else:
        try:
            # list dainfo 
            if id_user.role.role_en == "idcer":
                mList = DailyInfo.objects.extra(where=[sql_where]).order_by('-dainfo_create_time')
            else:
                mList = DailyInfo.objects.all().order_by('-dainfo_create_time')
        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))

    try:
        mList = SelfPaginator(request,mList, 20)
    except Exception,ex:
        logger.error("Exception: %s" %(str(ex)))
        mList = []
    kwvars = {
        'lPage':mList,
        'request':request,
        'form':form,
        'title':'工单系统-日常工单-列表',
        'title_content':'日常工单',
        'postUrl':'/workorder/dailywo/list/',
        'button_type':'add',
    }
    return render_to_response('workorder/dailywoList.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def dailywoAdd(request):
    """ dailywo add

    Function: 
        dailywo add
    Author:
        liuzhen210490@sogou-inc.com
    """

    form = {}
    form['id_idc_list'] = IDCList.objects.filter(idc_enable = True)
    form['id_op_list'] = OperList.objects.filter(op_enable = True)
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-日常工单-增加新工单',
        'title_content':'添加日常工单',
        'postUrl':'/workorder/dailywo/add/',
        'preUrl':'/workorder/dailywo/list/',
        'button_type':'add',
    }
    if request.method == "POST":
        logger.info("request_post:%s" %(str(request.POST)))
        logger.error("request_files:%s" %(str(request.FILES)))
        attachs = request.FILES.getlist("fileupload")
        idc_list = request.POST.getlist('id_idc')
        id_user = request.user
        id_st =  StatusList.objects.get(st_en = "wait-receive")
        id_op = OperList.objects.get(id_op = int(request.POST["id_op"]))
        id_op_li = OperList.objects.get(id_op = int(request.POST["id_op_li"]))
        dainfo_affirm =  request.POST["dainfo_affirm"]
        dainfo_content = request.POST["dainfo_content"]
        form['checked_idc_list'] = [ int(x.encode('utf-8')) for x in idc_list ]
        if not idc_list:form['idc_errors'] = "操作机房不能为空"
        if not dainfo_content:form['content_errors'] = "工单详情不能为空"
        if not idc_list or not dainfo_content:
            return render_to_response('workorder/dailywoAdd.html',kwvars,RequestContext(request))
        
        # multi idc add
        for i_idc in idc_list:
            try:
                id_idc = IDCList.objects.get(id_idc = int(i_idc))
                flag, dainfo_code = DailyInfoOb().new(id_idc = id_idc, id_user= id_user, id_st = id_st,
                                                      id_op = id_op, id_op_li = id_op_li, 
                                                      dainfo_content = dainfo_content)
                if flag is True and dainfo_code:
                    logger.info("日常工单创建成功(dailywo_add_success):%s" %(dainfo_code))

                    # add new process startime
                    id_st_post = StatusList.objects.get(id_st = 7)
                    flag, desc = ProcessOb().new(pr_wocode = dainfo_code, id_user = request.user, id_st = id_st_post,pr_spare = '',pr_start_time=current_datetime,id_engi=None)
                    if flag is True:
                        logger.info("日常工单时间节点添加成功(process_add_success):%s %s\nDetail:%s" 
                                    %(dainfo_code,id_st_post,desc))
                    else:
                        logger.error("日常工单时间节点添加失败(process_add_fail):%s %s \nError Log:%s" 
                                     %(dainfo_code,id_st_post,desc))

                    # send SMS
                    #tels = id_idc.id_user.all()
                    tels = id_idc.id_user.filter(is_active = True)
                    tels = [item.u_mphone for item in tels]
                    iDailyInfo = DailyInfo.objects.get(dainfo_code = dainfo_code)
                    message = "日常工单:%s,%s" %(dainfo_code,''.join(iDailyInfo.id_op_li.op_cn.strip()))
                    #处理p标签
                    re_p=re.compile('<[^>]+>')
                    message2 = """日常工单:%s
操作类型: %s
操作详情: 
%s""" %(dainfo_code,iDailyInfo.id_op_li,re_p.sub('',iDailyInfo.dainfo_content))
                    logger.info("发送短信(sendsms):接收人(receivers)%s, 消息内容(message)%s" %(str(tels),str(message)))
                    sms_result = send_sms(tels=tels, desc=message)
                    if sms_result["code"] == 0:
                        logger.info("发送短信成功(sms_success)")
                    else:
                        logger.error("发送短信失败(sms_fail)")
                    logger.info("短信URL:%s,发送状态:%s" %(sms_result["url"], sms_result["desc"]))
                    # send qq group message
                    gnumber = id_idc.idc_qqg
                    qq_result = SmartQQ().send_group_message(gnumber = gnumber , content = message2)
                    if qq_result["code"] == 0:
                        logger.info("发送QQ群消息成功(qq_message_success)")
                    else:
                        logger.error("发送QQ群消息失败(qq_message_fail)")
                    logger.info("QQ消息URL:%s,发送状态:%s" %(qq_result["url"], qq_result["status"]))
                else:
                    logger.error("日常工单创建失败(dailywo_add_fail):%s" %(dainfo_code))
            except Exception, ex:
                logger.error("Exception:%s" %(str(ex)))
                return render_to_response('workorder/dailywoAdd.html',kwvars,RequestContext(request))

            # upload attach file
            attach_infos = []
            for item in attachs:
                path = "./upload/"
                i_attach = {}
                i_attach["filename"] = dainfo_code+"_"+item.name
                i_attach["filetype"] = item.content_type
                i_attach["filepath"] = path
                file_name = i_attach["filepath"] + i_attach["filename"]
                #upload
                flag, desc = file_upload(item, path, file_name)
                if flag is True:
                    logger.info("上传成功(attach_success):%s, %s" %(file_name, desc))
                else:
                    logger.error("上传失败(attach_fail):%s, %s" %(file_name, desc))
                attach_infos.append(i_attach)

            # add attach infos
            id_dainfo = DailyInfo.objects.get(dainfo_code = dainfo_code)
            for i_attach in attach_infos:
                flag, desc = DailywoAttachOb().new(id_dainfo = id_dainfo, attach_minetype = i_attach["filetype"],
                                                   attach_location = i_attach["filepath"], attach_filename = i_attach["filename"])
                if flag is True:
                    logger.info("附件记录成功(attach_info_success):%s" %(desc))
                else:
                    logger.error("附件记录失败(attach_info_fail):%s" %(desc))
        return HttpResponseRedirect('/workorder/dailywo/list')
    return render_to_response('workorder/dailywoAdd.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def dailywoView(request,ID):
    id_user = request.user
    iDailywo = DailyInfo.objects.get(id_dainfo = ID)
    #faults_old = iDailywo.id_fault.all()
    faults_old = DailyInfoFault.objects.filter(id_dainfo=ID)
    print faults_old
    try:
        if request.method == "POST":
            attachs = request.FILES.getlist("fileupload")
            logger.info("request_post:%s" %(str(request.POST)))
            # del request.session['form_token'] 

            # upload attach file
            attach_infos = []
            for item in attachs:
                path = "./upload/"
                i_attach = {}
                i_attach["filename"] = iDailywo.dainfo_code+"_"+item.name
                i_attach["filetype"] = item.content_type
                i_attach["filepath"] = path
                file_name = i_attach["filepath"] + i_attach["filename"]
                # upload
                flag, desc = file_upload(item, path, file_name)
                if flag is True:
                    logger.info("上传成功(attach_success):%s, %s" %(file_name, desc))
                else:
                    logger.error("上传失败(attach_fail):%s, %s" %(file_name, desc))
                attach_infos.append(i_attach)

            # add attach infos 
            # id_dainfo = DailyInfo.objects.get(dainfo_code = iDailywo.dainfo_code)
            for i_attach in attach_infos:
                flag, desc = DailywoAttachOb().new(id_dainfo = iDailywo, attach_minetype = i_attach["filetype"],
                                                   attach_location = i_attach["filepath"], 
                                                   attach_filename = i_attach["filename"])
                if flag is True:
                    logger.info("附件记录成功(attach_info_success):%s" %(desc))
                else:
                    logger.error("附件记录失败(attach_info_fail):%s" %(desc))

            # save remark content
            remark_content = request.POST.get("remark_content")
            if remark_content:
                flag, desc = RemarkOb().new(re_wocode = iDailywo.dainfo_code, mark_content = remark_content, id_user = id_user)
                if flag is True:
                    logger.info("备注记录成功(remark_success):%s" %(desc))
                else:
                    logger.error("备注记录失败(remark_fail):%s" %(desc))

            try:
                action = request.POST["action"]
                logger.info("POST动作:%s" %(action))
            except Exception,ex:
                action = "resolve"
                logger.info("POST动作:%s" %(action))

            # prevent repeat submit
            if request.session['form_token'] == action and request.session['form_token'] != "remark-add":
                raise

            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if action == "remark-add":
                return HttpResponseRedirect('/workorder/dailywo/view/%s/' %ID)
            elif action == "accept": # 接收
                id_st_post = StatusList.objects.get(id_st = 6)
            elif action == "process": # 处理
                id_st_post = StatusList.objects.get(id_st = 11)
            elif action == "resolve": # 解决
                id_st_post = StatusList.objects.get(id_st = 9)
            elif action == "interrupt": # 中断
                id_st_post = StatusList.objects.get(id_st = 4)
            elif action == "open": # 开启
                id_st_post = StatusList.objects.get(id_st = 6)
            elif action == "distribution": # 分派
                id_st_post = StatusList.objects.get(id_st = 7)
            elif action == "check-ok":
                id_st_post = StatusList.objects.get(id_st = 1)
            elif action == "check-fail":
                id_st_post = StatusList.objects.get(id_st = 7)

            # faults process(new/update)
            try:
                faults = request.POST.getlist("faults")
                descs = request.POST.getlist("fault_desc")
                if faults:
                    for i, item in enumerate(faults_old):
                        try:
                            #iDailywo.id_fault.remove(item.id_fault)
                            DailyInfoFault.objects.filter(id_fault = item.id_fault,
                                                          id_dainfo = ID).delete()
                            logger.info("删除故障类型成功(dainfofault_delete_success):%s %s" %(iDailywo.dainfo_code,item))
                        except Exception,ex:
                            logger.error("Exception: %s" %(str(ex)))
                    for i,item in enumerate(faults):
                        try:
                            #DailyInfoFault.objects.
                            id_fault = FaultList.objects.get(id_fault = item)
                            #iDailywo.id_fault.add(item)
                            flag, desc = DailyInfoFaultOb().new(id_fault = id_fault, dafault_desc = descs[i],
                                                                id_dainfo = iDailywo)
                            if flag is True:
                                logger.info("添加日常工单故障成功(dafault_add_success):%s %s\nDetail:%s" %(iDailywo.dainfo_code,item,desc))
                            else:
                                logger.error("添加日常工单故障失败(dafault_add_fail):%s %s\nDetail:%s" %(iDailywo.dainfo_code,item,desc))
                        except Exception, ex:
                            logger.error("Exception: %s" %(str(ex)))
            except Exception, ex:
                logger.error("Exception: %s" %(str(ex)))
            if action != "remark-add":
                DailyInfo.objects.filter(id_dainfo=ID).update(id_st = id_st_post)
                #change process endtime
                Process.objects.filter(pr_wocode = iDailywo.dainfo_code, pr_end_time = F('pr_start_time')).update(pr_end_time = current_datetime)
                #add new process startime
                flag, desc = ProcessOb().new(pr_wocode = iDailywo.dainfo_code, id_user = request.user, id_st = id_st_post,pr_spare='',pr_start_time=current_datetime,id_engi=None)
                if flag is True:
                    logger.info("日常工单时间节点添加成功(process_add_success):%s %s\nDetail:%s" %(iDailywo.dainfo_code,id_st_post,desc))
                else:
                    logger.error("日常工单时间节点添加失败(process_add_fail):%s %s \nError Log:%s" %(iDailywo.dainfo_code,id_st_post,desc))

            request.session['form_token'] = action
            return HttpResponseRedirect('/workorder/')
        else:
            request.session['form_token'] = "helloworld"
    except Exception,ex:
        logger.error("Exception: %s" %(str(ex)))
        return HttpResponseRedirect('/workorder/dailywo/view/%s/' %ID)
    iDailywo = DailyInfo.objects.get(id_dainfo =ID)
    remarks = Remark.objects.filter( re_wocode = iDailywo.dainfo_code )
    attachs = DailywoAttach.objects.filter(id_dainfo = iDailywo)
    timeline = Process.objects.filter( pr_wocode = iDailywo.dainfo_code )
    faults = FaultList.objects.all()
    kwvars = {
        'current_user':id_user,
        'timeline':timeline,
        'faults':faults,
        'faults_old':faults_old,
        'attachs':attachs,
	'form':iDailywo,
        'remarks':remarks,
        'request':request,
        'title':'工单系统-报修工单-编辑报修工单',
        'title_content':'编辑报修工单',
        'postUrl':'/workorder/dailywo/view/%s/' %ID,
        'preUrl':'/workorder/dailywo/list/',
        'button_type':'update',
    }
    return render_to_response('workorder/dailywoView.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def dailywoEdit(request,ID):
    iDailywo = DailyInfo.objects.get(id_dainfo=ID)
    form = {}
    form['id_idc_list'] = IDCList.objects.filter(idc_enable = True)
    form['id_op_list'] = OperList.objects.filter(op_enable = True)
    if request.method == "POST":
        logger.info("request_post:%s" %(str(request.POST)))
        try:
            action = request.POST.get("action")
            attach = action.split('-')[1]
            action = action.split('-')[0]
        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))
            action = ""
            attach = ""
            logger.error("request_files:"+str(request.FILES))
            attachs = request.FILES.getlist("fileupload")
            id_idc = IDCList.objects.get(id_idc = int(request.POST['id_idc']))
            id_op = OperList.objects.get(id_op = int(request.POST["id_op"]))
            id_op_li = OperList.objects.get(id_op = int(request.POST["id_op_li"]))
            dainfo_affirm =  request.POST["dainfo_affirm"]
            dainfo_content = request.POST["dainfo_content"]

            # upload attach file
            attach_infos = []
            for item in attachs:
                path = "./upload/"
                i_attach = {}
                i_attach["filename"] = iDailywo.dainfo_code+"_"+item.name
                i_attach["filetype"] = item.content_type
                i_attach["filepath"] = path
                file_name = i_attach["filepath"] + i_attach["filename"]
                # upload
                flag, desc = file_upload(item, path, file_name)
                if flag is True:
                    logger.info("上传成功(attach_success):%s, %s" %(file_name, desc))
                else:
                    logger.error("上传失败(attach_fail):%s, %s" %(file_name, desc))
                attach_infos.append(i_attach)

            # add attach infos 
            # id_dainfo = DailyInfo.objects.get(dainfo_code = iDailywo.dainfo_code)
            for i_attach in attach_infos:
                flag, desc = DailywoAttachOb().new(id_dainfo = iDailywo, attach_minetype = i_attach["filetype"],
                                                   attach_location = i_attach["filepath"], 
                                                   attach_filename = i_attach["filename"])
                if flag is True:
                    logger.info("附件记录成功(attach_info_success):%s" %(desc))
                else:
                    logger.error("附件记录失败(attach_info_fail):%s" %(desc))

        # delete attach
        if action == "attachdel":
            DailywoAttach.objects.filter(id_attach = attach).delete()
        # update dailyinfo detail 
        else:
            DailyInfo.objects.filter(id_dainfo = ID).update(id_idc = id_idc,\
                                       id_op = id_op,id_op_li = id_op_li,\
                                       dainfo_affirm = dainfo_affirm,\
                                       dainfo_content = dainfo_content)
            return HttpResponseRedirect('/workorder/dailywo/list')

    iDailywo = DailyInfo.objects.get(id_dainfo=ID)
    attachs = DailywoAttach.objects.filter(id_dainfo = iDailywo)
    kwvars = {
	'form':form,
        'attachs':attachs,
        'request':request,
        'title':'工单系统-日常工单-编辑日常工单',
        'title_content':'编辑日常工单',
        'postUrl':'/workorder/dailywo/edit/%s/' %ID,
        'preUrl':'/workorder/dailywo/list/',
        'button_type':'update',
        'iDailywo' : iDailywo,
    }
    return render_to_response('workorder/dailywoEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def dailywoDel(request,ID):
    DailyInfo.objects.filter(id_dainfo = ID).delete()
    return HttpResponseRedirect('/workorder/dailywo/list/')


@login_required()
@IpaddressAcl()
@PermissionVerify()
def repairwoList(request):
    form = {}
    form['id_idc_list'] = IDCList.objects.filter(idc_enable = True )
    form['id_st_list'] = StatusList.objects.filter(st_enable = True)
    form['id_model_list'] = ModelList.objects.filter(model_enable = True)
    form['id_fault_list'] = FaultList.objects.filter(fault_enable = True)
    id_user = request.user
    if request.method == "POST":
        logger.info("request_post:%s" %(str(request.POST)))
        try:
            # search
            query_dic = {}
            #query_dic["reinfo_code__contains"] = request.POST["reinfo_code"]
            query_dic["id_idc"] = request.POST["id_idc"]
            query_dic["id_model"] = request.POST["id_model"]
            query_dic["re_sn__contains"] = request.POST["re_sn"]
            query_dic["id_st"] = request.POST["id_st"]
            Q_dic = Q()
            id_idcs = id_user.idc_users.all()
            id_idcs = [int(idc.id_idc) for idc in id_idcs]
            id_idcs = tuple(id_idcs)
            if len(id_idcs) == 1: sql_where = 'id_idc_id = %s' %(id_idcs[0])
            else: sql_where = 'id_idc_id in '+ str(id_idcs)
            id_fault = request.POST["id_fault"]

            for key in query_dic.keys():
                if query_dic[key]:Q_dic.add(Q(**{key:query_dic[key]}),Q.AND)
            if id_user.role.role_en == "sogouer" or id_user.role.role_en == "Admin" or id_user.role.role_en == "daily_wo":
                mList = RepairInfo.objects.filter(Q_dic).order_by('-re_create_time')
            elif id_user.role.role_en == "idcer":
                mList = RepairInfo.objects.filter(Q_dic).extra(where=[sql_where]).order_by('-re_create_time')
        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))
            #mList = RepairInfo.objects.filter(Q_dic).order_by('-re_create_time')
    else:
        try:
            id_idcs = id_user.idc_users.all()
            id_idcs = [int(idc.id_idc) for idc in id_idcs]
            id_idcs = tuple(id_idcs)
            if len(id_idcs) == 1: sql_where = 'id_idc_id = %s' %(id_idcs[0])
            else: sql_where = 'id_idc_id in '+str(id_idcs)
            if id_user.role.role_en == "sogouer" or id_user.role.role_en == "Admin" or id_user.role.role_en == "daily_wo":
                mList = RepairInfo.objects.all().order_by('-re_create_time')
            elif id_user.role.role_en == "idcer":
                mList = RepairInfo.objects.all().extra(where=[sql_where]).order_by('-re_create_time')
        except Exception,ex:
            logger.error("Exception: %s" %(str(ex)))
            #mList = RepairInfo.objects.all().order_by('-re_create_time')
            mList = []
    nmList = []
    try:
        # filter fault type
        for item in mList:
            if RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo).filter(id_fault = id_fault):
                tmp = [item,RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo)]
                nmList.append(tmp)
        mList = SelfPaginator(request,nmList, 20)
    except Exception,ex:
        for item in mList:
            tmp = [item,RepairInfoFault.objects.filter(id_reinfo=item.id_reinfo)]
            nmList.append(tmp)
        mList = SelfPaginator(request,nmList, 20)
        print mList
        #logger.error("Exception: %s" %(str(ex)))
        #mList = []
    kwvars = {
        'form':form,
        'lPage':mList,
        'request':request,
        'postUrl':'/workorder/repairwo/list/',
        'title':'工单系统-报修工单-列表',
        'title_content':'报修工单',
        'button_type':'add',
    }
    return render_to_response('workorder/repairwoList.html',kwvars,RequestContext(request))



@login_required()
@IpaddressAcl()
@PermissionVerify()
def repairwoAdd(request):
    form = {}
    form['id_idc_list'] = IDCList.objects.filter(idc_enable = True )
    form['id_model_list'] = ModelList.objects.filter(model_enable = True)
    form['id_fault_list'] = FaultList.objects.filter(fault_enable = True)
    form['id_spare_list'] = SpareList.objects.filter(spare_enable = True)
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if request.method == "POST":
        logger.info("request_post:%s" %(str(request.POST)))
        id_user = request.user
        id_st =  StatusList.objects.get(st_en = "wait-receive")
        id_idc = IDCList.objects.get(id_idc = request.POST.get("id_idc"))
        id_model = ModelList.objects.get(id_model = request.POST.get("id_model"))
        rock = request.POST.get("rock")
        sn = request.POST.get("sn")
        id_faults = request.POST.getlist("id_fault") 
        fault_descs = request.POST.getlist("fault_desc")
        re_content = request.POST.get("re_content")
        flag, reinfo_code = RepairInfoOb().new(id_user = id_user, id_st = id_st, id_idc = id_idc, 
                                               id_model = id_model, re_rock = rock, re_sn = sn, 
                                               re_content = re_content)
        if flag is True:
            logger.info("报修工单创建成功(repairwo_add_success):%s %s" %(reinfo_code, re_content))
        else:
            logger.error("报修工单添加失败(repairwo_add_fail):Error Log:%s" %(reinfo_code))

        #add new process startime
        id_st_post = StatusList.objects.get(id_st = 7)
        flag, desc = ProcessOb().new(pr_wocode = reinfo_code, id_user = request.user, id_st = id_st_post,pr_spare='',pr_start_time=current_datetime,id_engi=None)
        if flag is True:
            logger.info("日常工单时间节点添加成功(process_add_success):%s %s\nDetail:%s" %(reinfo_code,id_st_post,desc))
        else:
            logger.error("日常工单时间节点添加失败(process_add_fail):%s %s \nError Log:%s" %(reinfo_code,id_st_post,desc))

        # send sms
        iRepairInfo = RepairInfo.objects.get(reinfo_code = reinfo_code)
        #tels = id_idc.id_user.all()
        tels = id_idc.id_user.filter(is_active = True)
        tels = [item.u_mphone for item in tels]
        message = "报修工单:%s,机型:%s,SN:%s,机架位:%s" %(reinfo_code,iRepairInfo.id_model.id_brand.brand_en+"-"+'-'.join(iRepairInfo.id_model.model_en.split()),iRepairInfo.re_sn,iRepairInfo.re_rock)
        sms_result = send_sms(tels=tels, desc=message)
        logger.info("发送短信(sendsms):接收人(receivers)%s, 消息内容(message)%s" %(str(tels),str(message)))
        if sms_result["code"] == 0:
            logger.info("发送短信成功(sms_success)")
        else:
            logger.error("发送短信失败(sms_fail)")
        logger.info("短信URL:%s,发送状态:%s" %(sms_result["url"], sms_result["desc"]))

        # send qq group message
        gnumber = id_idc.idc_qqg
        message2 = """报修工单: {0}, 
机型: {1}, SN: {2}, 机架位: {3}""".format(reinfo_code, iRepairInfo.id_model.id_brand.brand_en+"-"+'-'.join(iRepairInfo.id_model.model_en.split()), 
                       iRepairInfo.re_sn,iRepairInfo.re_rock)
        qq_result = SmartQQ().send_group_message(gnumber = gnumber , content = message2)
        if qq_result["code"] == 0:
            logger.info("发送QQ群消息成功(qq_message_success)")
        else:
            logger.error("发送QQ群消息失败(qq_message_fail)")
        logger.info("QQ消息URL:%s,发送状态:%s" %(qq_result["url"], qq_result["status"]))

        for i in xrange(len(id_faults)):
            try:
                id_fault = FaultList.objects.get(id_fault = id_faults[i])
                fault_desc = fault_descs[i]
            except Exception, ex:
                logger.error("Exception: %s" %(str(ex)))
                id_fault = 0
                fault_desc = ""
            #flag, desc = RepairInfoFaultOb().new(id_reinfo = iRepairInfo ,id_fault = id_fault ,refault_desc = fault_desc)
            #if flag is True:
            #    logger.info("报修故障记录成功(repair_fault_success):%s" %(desc))
            #else:
            #    logger.error("报修故障记录失败(repair_fault_fail):%s" %(desc))
        return HttpResponseRedirect('/workorder/repairwo/list')
    kwvars = {
        'form':form,
        'request':request,
        'title':'工单系统-报修工单-添加报修工单',
        'postUrl':'/workorder/repairwo/add/',
        'preUrl':'/workorder/repairwo/list/',
        'title_content':'添加报修工单',
        'button_type':'add',
    }
    return render_to_response('workorder/repairwoAdd.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def repairwoEdit(request,ID):
    form = {}
    form['id_idc_list'] = IDCList.objects.filter(idc_enable = True )
    form['id_model_list'] = ModelList.objects.filter(model_enable = True)
    form['id_fault_list'] = FaultList.objects.filter(fault_enable = True)
    form['id_spare_list'] = SpareList.objects.filter(spare_enable = True)
    iRepairwo = RepairInfo.objects.get(id_reinfo=ID)
    iRepairwoFaults = RepairInfoFault.objects.filter(id_reinfo=iRepairwo)
    if request.method == "POST":
        logger.info("request_post:%s" %(str(request.POST)))
        reinfo_code = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        id_user = request.user
        id_st =  StatusList.objects.get(st_en = "wait-receive")
        id_idc = IDCList.objects.get(id_idc = request.POST.get("id_idc"))
        id_model = ModelList.objects.get(id_model = request.POST.get("id_model"))
        rock = request.POST.get("rock")
        sn = request.POST.get("sn")
        re_content = request.POST.get("re_content")
        RepairInfo.objects.filter(id_reinfo = ID).update(id_idc = id_idc, id_model = id_model, re_sn = sn, 
                                                         re_rock = rock, re_content = re_content)
        id_faults = request.POST.getlist("id_fault") 
        fault_descs = request.POST.getlist("fault_desc")
        RepairInfoFault.objects.filter(id_reinfo = iRepairwo).delete()
        for i in xrange(len(id_faults)):
            id_fault = FaultList.objects.get(id_fault = id_faults[i])
            fault_desc = fault_descs[i]
            flag, desc = RepairInfoFaultOb().new(id_reinfo = iRepairwo ,id_fault = id_fault ,refault_desc = fault_desc)
            if flag is True:
                logger.info("报修故障记录成功(repair_fault_success):%s" %(desc))
            else:
                logger.error("报修故障记录失败(repair_fault_fail):%s" %(desc))
        return HttpResponseRedirect('/workorder/repairwo/list')

    kwvars = {
	'form':form,
        'request':request,
        'title':'工单系统-报修工单-编辑报修工单',
        'title_content':'编辑报修工单',
        'postUrl':'/workorder/repairwo/edit/%s/' %ID,
        'preUrl':'/workorder/repairwo/list/',
        'button_type':'update',
        'iRepairwo' : iRepairwo,
        'iRepairwoFaults':iRepairwoFaults,
    }
    return render_to_response('workorder/repairwoEdit.html',kwvars,RequestContext(request))


# @login_required()
# @IpaddressAcl()
# @PermissionVerify()
# def repairwoAddSpare(request,ID):
#     try:
#         if request.method == "POST":
#             logger.info("request_post:%s" %(str(request.POST)))
#             #del request.session['form_token']
#             remark_content = request.POST.get("remark_content")

@login_required()
@IpaddressAcl()
@PermissionVerify()
def repairwoView(request,ID):
    id_user = request.user
    iRepairwo = RepairInfo.objects.get(id_reinfo = ID)
    iRepairwoFaults = RepairInfoFault.objects.filter(id_reinfo = iRepairwo)
    id_fault_list_php = json.loads(urllib.urlopen('http://if01.sat.sac.sogou/bzh/repair_info.php').read())['val']['hard_type']
    Q_dic = Q()
    id_brand = iRepairwo.id_model.id_brand_id
    id_idcs = id_user.idc_users.all()
    id_idcs = [idc.idc_en for idc in id_idcs]
    for idc in id_idcs:
        if idc: Q_dic.add(Q(**{"engineer_zone": idc.split('-')[0]}), Q.OR)
    Q_dic.add(Q(**{"id_brand": id_brand}), Q.AND)
    engineers = EngineerList.objects.filter(Q_dic)
    # 二次上门时，默认时间就为第一次的时间
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    try: 
        if request.method == "POST":
            id_fault_dict = {}
            for key, value in id_fault_list_php.items():
                id_fault_dict[key] = value.decode()

            logger.info("request_post:%s" %(str(request.POST)))
            #del request.session['form_token'] 
            remark_content = request.POST.get("remark_content")

            # add new remark
            if remark_content:
                flag, desc = RemarkOb().new(re_wocode = iRepairwo.reinfo_code, mark_content = remark_content, id_user = id_user)
                if flag is True:
                    logger.info("备注记录成功(remark_success):%s" %(desc))
                else:
                    logger.error("备注记录失败(remark_fail):%s" %(desc))
            try:
                action = request.POST["action"]
                logger.info("POST动作:%s" %(action))
            except Exception,ex:
                action = "resolve"
                logger.info("POST动作:%s" %(action))
            if request.session['form_token'] == action and request.session['form_token'] != "remark-add":
                raise
            if action == "remark-add":
                return HttpResponseRedirect('/workorder/repairwo/view/%s/' %ID)
            #首次接收上门
            elif action == 'first_doortime':
                id_st = 12
                if Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st=id_st):
                    msg='首次上门只允许点击一下，重复点击不生效！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                id_st_post = StatusList.objects.get(id_st=id_st)
                SpareLackContent = request.POST.get('SpareLackContent')
                come_time = request.POST.get('come_time')
                id_engineer = request.POST.get('id_engineer')
                id_faults = request.POST.getlist('id_fault')
                id_fault = ''
                id_fault_value = ''
                for i in id_faults:
                    id_fault_value += id_fault_dict[i] + ','
                    id_fault += i + ','
                id_fault = id_fault[:-1]
                id_fault_value = id_fault_value[:-1]
                if not id_faults or not come_time or not id_engineer:
                    msg = '请选择首次上门，工程师所携带的备件类型、上门时间、工程师！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                engineer = EngineerList.objects.get(id_engineer=id_engineer)
                post_dict = {'repair_id': iRepairwo.reinfo_code, 'first_doortime': str(come_time),'spare_type':id_fault,'engineer':engineer.engineer_cn}
                status = 'first_doortime'
                repairwoView_post_statustime(post_dict, iRepairwo, id_st_post, status)
                id_st_post = repairwoView_createprocess(id_st, iRepairwo, come_time, request, ID,id_fault_value,engineer)
                return HttpResponseRedirect('/workorder/repairwo/view/%s/' % ID)

            #二次上门处理
            elif action == 'second_doortime':
                F_state = Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='13')
                L_state = Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='14')
                if not Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='12'):
                    msg = '首次上门还未点击，请先点首次上门！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                elif not Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='14'):
                    msg = '首次上门后，需点击离开时间，请保证上门的次数和离开次数相同！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                elif F_state.__len__() - L_state.__len__() >= 0:
                    msg = '二次上门后，需点击离开时间后，请保证上门的次数和离开次数相同！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                id_st = 13
                id_st_post = StatusList.objects.get(id_st=id_st)
                SpareLackContent = request.POST.get('SpareLackContent')
                id_faults = request.POST.getlist('id_fault')
                re_come_time = request.POST.get('re_come_time')
                id_engineer = request.POST.get('id_engineer')
                id_fault = ''
                id_fault_value = ''
                for i in id_faults:
                    id_fault_value += id_fault_dict[i] + ','
                    id_fault += i + ','
                id_fault = id_fault[:-1]
                id_fault_value = id_fault_value[:-1]
                if not id_faults or not re_come_time or not id_engineer:
                    msg = '请选择二次上门，工程师所携带的备件类型、上门时间、工程师！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                engineer = EngineerList.objects.get(id_engineer=id_engineer)
                post_dict = {'repair_id': iRepairwo.reinfo_code, 'second_doortime': str(re_come_time),'spare_type':id_fault,'engineer':engineer.engineer_cn}
                status = 'second_doortime'
                repairwoView_post_statustime(post_dict, iRepairwo, id_st_post, status)
                id_st_post = repairwoView_createprocess(id_st, iRepairwo, re_come_time, request, ID,id_fault_value,engineer)
                return HttpResponseRedirect('/workorder/repairwo/view/%s/' % ID)


            #离开时间
            elif action == 'leave_time':
                leave_time = request.POST.get('leave_time')
                F_state = Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='13')
                L_state = Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='14')
                if not Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='12'):
                    msg = '首次上门还未点击，请先点首次上门，工程师处理完后，再点击离开时间！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                elif  L_state.__len__() - F_state.__len__()  >= 1:
                    msg = '请先点击二次上门后再点击离开时间，请保证上门的次数和离开次数相同！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                id_st = 14
                id_fault_value = '故障未处理完'
                id_st_post = StatusList.objects.get(id_st=id_st)
                # post_dict = {'repair_id': iRepairwo.reinfo_code, 'solve_time': str(leave_time)}
                # status = 'solve_time'
                # repairwoView_post_statustime(post_dict, iRepairwo, id_st_post, status)
                id_st_post = repairwoView_createprocess(id_st, iRepairwo, leave_time, request, ID,id_fault_value,engineer=None)
                return HttpResponseRedirect('/workorder/repairwo/view/%s/' % ID)


            elif action == 'spare_lack':
                id_st = 15
                id_st_post = StatusList.objects.get(id_st=id_st)
                SpareLackContent = request.POST.get('SpareLackContent')
                id_faults = request.POST.getlist('id_fault')
                if not id_faults :
                    msg = '请选择缺少备件的类型！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                id_fault = ''
                id_fault_value =''
                for i in id_faults:
                    id_fault_value += id_fault_dict[i] +','
                    id_fault += i + ','
                id_fault=id_fault[:-1]
                id_fault_value=id_fault_value[:-1]
                post_dict = {'repair_id': iRepairwo.reinfo_code, 'lack_of_spare': current_datetime,'spare_type':id_fault}
                status = 'lack_of_spare'
                repairwoView_post_statustime(post_dict, iRepairwo, id_st_post, status)

                id_st_post = repairwoView_createprocess(id_st, iRepairwo, current_datetime, request, ID,id_fault_value,engineer=None)
                return HttpResponseRedirect('/workorder/repairwo/view/%s/' % ID)
            # accept order 接收工单
            elif action == "accept":
                id_st_post = StatusList.objects.get(id_st = 8)
                id_fault_value ='等待处理'
                id_faulttype = None
                flag, desc = ProcessOb().new(pr_wocode=iRepairwo.reinfo_code, id_user=request.user, id_st=id_st_post,pr_spare=id_fault_value,pr_start_time=current_datetime,id_engi=None)
                if flag is True:
                    logger.info(
                        "报修工单时间节点添加成功(process_add_success):%s %s\nDetail:%s" % (iRepairwo.reinfo_code, id_st_post, desc))
                else:
                    logger.error(
                        "报修工单时间节点添加失败(process_add_fail):%s %s \nError Log:%s" % (iRepairwo.reinfo_code, id_st_post, desc))

            # resolve order 故障解决
            elif action == "resolve":
                if not Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='12'):
                    msg = '首次上门必须点击，才可以点离开时间！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                id_faults = request.POST.getlist('id_fault')
                leave_time = request.POST.get('leave_time')
                id_faulttype = request.POST.get('id_faulttype')
                if not id_faults or not leave_time or not id_faulttype :
                    msg = '请选择工程师是通过更换备件或其他操作解决的故障和离开时间！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                F_state = Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='13')
                L_state = Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='14')
                if not Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='12'):
                    msg = '首次上门还未点击，请先点首次上门，工程师处理完后，再点击离开时间！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                elif L_state.__len__() - F_state.__len__() >= 1:
                    msg = '请先点击二次上门后再点击离开时间，请保证上门的次数和离开次数相同！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                id_st = 14
                id_st_post = StatusList.objects.get(id_st=id_st)
                SpareLackContent = request.POST.get('SpareLackContent')
                id_fault = ''
                id_fault_value = ''
                for i in id_faults:
                    id_fault_value += id_fault_dict[i] + ','
                    id_fault += i + ','
                id_fault = id_fault[:-1]
                id_fault_value = id_fault_value[:-1]
                id_st_post = repairwoView_createprocess(id_st, iRepairwo, leave_time, request, ID, id_fault_value,engineer=None)
                id_st = 9
                id_st_post = StatusList.objects.get(id_st=id_st)
                idc_comment = FaultTypeList.objects.get(id_faulttype=id_faulttype)
                post_dict = {'repair_id': iRepairwo.reinfo_code, 'solve_time': str(leave_time),'spare_type': id_fault,'idc_comment':idc_comment.faulttype_en}
                status = 'solve_time'
                repairwoView_post_statustime(post_dict, iRepairwo, id_st_post, status)
                id_st_post = repairwoView_createprocess(id_st, iRepairwo, leave_time, request, ID,id_fault_value,engineer=None)

            #外包自己解决故障
            elif action == "resolve_self":
                if  Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st='12'):
                    msg = '请选择工程师上门处理方式，点击离开时间,提交保修工单！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                id_faults = request.POST.getlist('id_fault')
                if not id_faults:
                    msg = '请选择工程师解决故障的方式！'
                    return repairwoView_return(id_user, current_datetime, iRepairwoFaults, request, ID, msg)
                id_st = 9
                id_faulttype = None
                id_st_post = StatusList.objects.get(id_st=id_st)
                SpareLackContent = request.POST.get('SpareLackContent')
                id_fault = ''
                id_fault_value = ''
                for i in id_faults:
                    id_fault_value += id_fault_dict[i] + ','
                    id_fault += i + ','
                id_fault = id_fault[:-1]
                id_fault_value = id_fault_value[:-1]
                post_dict = {'repair_id': iRepairwo.reinfo_code, 'solve_time': current_datetime, 'spare_type': id_fault}
                status = 'solve_time'
                repairwoView_post_statustime(post_dict, iRepairwo, id_st_post, status)
                id_st_post = repairwoView_createprocess(id_st, iRepairwo, current_datetime, request, ID,id_fault_value,engineer=None)
            # 验收通过
            elif action == "check-ok":
                id_st = 1
                id_faulttype = None
                id_fault_value='验收通过'
                id_st_post = repairwoView_createprocess(id_st, iRepairwo, current_datetime, request, ID,id_fault_value,engineer=None)

            # 验收不通过
            elif action == "check-fail":
                id_st = 7
                id_faulttype = None
                id_fault_value='验收不通过'
                id_st_post = repairwoView_createprocess(id_st, iRepairwo, current_datetime, request, ID,id_fault_value,engineer=None)


            #工单流程转变
            if action != "remark-add" or action != "first_doortime" or action != "second_doortime" or action != "leave_time" or action != "spare_lack":
                id_faulttype = id_faulttype if id_faulttype else None
                RepairInfo.objects.filter(id_reinfo=ID).update(id_st = id_st_post,id_faulttype=id_faulttype)  #修改工单状态

            request.session['form_token'] = action
            return HttpResponseRedirect('/workorder/')
        else:
            request.session['form_token'] = "helloworld"
    except Exception,ex:
        print ex
        logger.error("Exception: %s" %(str(ex)))
        return HttpResponseRedirect('/workorder/repairwo/view/%s/' %ID)
    faulttypes = FaultTypeList.objects.filter(faulttype_enable=True)
    iRepairwo = RepairInfo.objects.get(id_reinfo=ID)
    remarks = Remark.objects.filter( re_wocode = iRepairwo.reinfo_code )
    timeline = Process.objects.filter( pr_wocode = iRepairwo.reinfo_code )
    timelinespare = SpareLack.objects.filter(id_reinfo_id = ID)
    todoortime =  Process.objects.filter( pr_wocode = iRepairwo.reinfo_code,id_st_id=12)
    timerepair = timeline[0].id_st

    kwvars = {
        'current_user':id_user,
        'current_datetime':current_datetime,
        'iRepairwoFaults':iRepairwoFaults,
        'form':iRepairwo,
        'remarks':remarks,
        'timeline':timeline,
        'timelinespare':timelinespare,
        'todoortime':todoortime,
        'id_fault_list_php':id_fault_list_php,
        'engineers':engineers,
        'faulttypes':faulttypes,
        'request':request,
        'title':'工单系统-报修工单-编辑报修工单',
        'title_content':'编辑报修工单',
        'postUrl':'/workorder/repairwo/view/%s/' %ID,
        'preUrl':'/workorder/repairwo/list/',
        'button_type':'update',
    }
    # 状态为待处理时，需要修改上门时间
    return render_to_response('workorder/repairwoView.html',kwvars,RequestContext(request))


def repairwoView_createprocess(id_st,iRepairwo,current_datetime,request,ID,pr_spare,engineer):
    id_st_post = StatusList.objects.get(id_st=id_st)
    Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, pr_end_time=F('pr_start_time')).update(
        pr_end_time=current_datetime)
    flag, desc = ProcessOb().new(pr_wocode=iRepairwo.reinfo_code, id_user=request.user, id_st=id_st_post,pr_spare=pr_spare,pr_start_time=current_datetime,id_engi=engineer)
    if flag is True:
        logger.info("报修工单时间节点添加成功(process_add_success):%s %s\nDetail:%s" % (iRepairwo.reinfo_code, id_st_post, desc))
    else:
        logger.error("报修工单时间节点添加失败(process_add_fail):%s %s \nError Log:%s" % (iRepairwo.reinfo_code, id_st_post, desc))
    return id_st_post


def repairtimeView(atime):
    timerepair_secs = time.mktime(atime.timetuple())




def repairwoView_return(id_user,current_datetime,iRepairwoFaults,request,ID,msg):
    iRepairwo = RepairInfo.objects.get(id_reinfo=ID)
    remarks = Remark.objects.filter(re_wocode=iRepairwo.reinfo_code)
    timeline = Process.objects.filter(pr_wocode=iRepairwo.reinfo_code)
    timelinespare = SpareLack.objects.filter(id_reinfo_id=ID)
    todoortime = Process.objects.filter(pr_wocode=iRepairwo.reinfo_code, id_st_id=12)
    id_fault_list_php = json.loads(urllib.urlopen('http://if01.sat.sac.sogou/bzh/repair_info.php').read())['val']['hard_type']
    Q_dic = Q()
    id_brand = iRepairwo.id_model.id_brand_id
    id_idcs = id_user.idc_users.all()
    id_idcs = [idc.idc_en for idc in id_idcs]
    for idc in id_idcs:
        if idc: Q_dic.add(Q(**{"engineer_zone": idc.split('-')[0]}), Q.OR)
    Q_dic.add(Q(**{"id_brand": id_brand}), Q.AND)
    engineers = EngineerList.objects.filter(Q_dic)

    kwvars = {
        'msg': msg,
        'current_user': id_user,
        'current_datetime': current_datetime,
        'iRepairwoFaults': iRepairwoFaults,
        'form': iRepairwo,
        'remarks': remarks,
        'timeline': timeline,
        'timelinespare':timelinespare,
        'todoortime': todoortime,
        'id_fault_list_php': id_fault_list_php,
        'engineers': engineers,
        'request': request,
        'title': '工单系统-报修工单-编辑报修工单',
        'title_content': '编辑报修工单',
        'postUrl': '/workorder/repairwo/view/%s/' % ID,
        'preUrl': '/workorder/repairwo/list/',
        'button_type': 'update',
    }
    # 状态为待处理时，需要修改上门时间
    return render_to_response('workorder/repairwoView.html', kwvars, RequestContext(request))


def repairwoView_post_statustime(post_dict,iRepairwo,id_st_post,status):
    post_data = urllib.urlencode(post_dict)
    URL_ACT_ORDER = "http://ias.sogou/repair/updetail"
    try:
        ret_dict = urllib_get(URL_ACT_ORDER, post_data)
        if ret_dict['ret'] == True:
            print "报修工单时间节点添加成功(add_%s):%s %s %s" % (status,iRepairwo.reinfo_code, id_st_post,post_dict)
            logger.info("报修工单时间节点添加成功(add_%s):%s %s %s" % (status,iRepairwo.reinfo_code, id_st_post,post_dict))
        else:
            logger.info("报修工单时间节点添加失败(add_%s):%s %s %s" % (status,iRepairwo.reinfo_code, id_st_post,post_dict))
    except Exception, e:
        logger.error("报修工单时间节点添加错误(add_%s):%s %s %s" % (status,iRepairwo.reinfo_code, repr(e),post_dict))



@login_required()
@IpaddressAcl()
@PermissionVerify()
def repairwoDel(request,ID):
    RepairInfo.objects.filter(id_reinfo = ID).delete()
    return HttpResponseRedirect('/workorder/repairwo/list/')

def dailywoTest(request):
    if request.method == "POST":
        logger.info("request_post:%s" %(str(request.POST)))
        print request.FILES
    kwvars = {
        'request':request,
        'title':'工单系统-日常工单-编辑日常工单',
        'title_content':'编辑日常工单',
        'postUrl':'/workorder/dailywo/add/',
        'preUrl':'/workorder/dailywo/list/',
        'button_type':'update',
    }
    return render_to_response('workorder/test.html',kwvars,RequestContext(request))

