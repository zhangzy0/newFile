#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""功能描述
@filename:
@author:
@date:
@version:
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from apps.usermanage.views.permission import PermissionVerify
from apps.workorder.models import Commute, CommexAttach, CommuteExplain
from django.views.decorators.csrf import csrf_exempt
from plugins.codegit.file_oper import file_upload
from plugins.myclass.commute_models import CommuteExplainOb, CommexAttachOb
from website.common.CommonPaginator import SelfPaginator
import json
import logging
import time

logger = logging.getLogger('workorder')


@login_required
@PermissionVerify()
def getCommute(request):
    response_data = {}
    idate = request.GET["idate"]
    response_data["ret_code"] = 1
    response_data["ret_info"] = {}
    response_data["ret_info"]["idate"] = idate
    response_data["ret_info"]["icommute"] = ""
    try:
        icommute = Commute.objects.get(comm_date=idate, id_user=request.user)
        response_data["ret_info"]["icommute"] = {
            "worktime": str(icommute.comm_worktime),
            "offtime": str(icommute.comm_offtime)
        }
    except Exception, ex:
        response_data["ret_code"] = 0
    return HttpResponse(
        json.dumps(response_data), content_type="application/json")


@login_required
@PermissionVerify()
def getCommuteExplainList(request):
    if request.method == "GET":
        try:
            pagesize = request.GET["pagesize"]
        except:
            pagesize = 25
        mList = CommuteExplain.objects.filter(id_user = request.user).order_by('-commex_create_time')
        lst = SelfPaginator(request,mList, pagesize)
        result = {}
        result["total"] = len(mList)
        result["rows"] = []
        for lid,item in enumerate(lst.object_list):
            t_result = {}
            t_result["id"] = lid+1
            t_result["commex_apply_date"] = str(item.commex_date)
            t_result["commex_status"] = item.commex_status
            t_result["commex_result"] = item.commex_result
            t_result["commute_date"] = str(item.commute_commex.all())
            t_result["commute_worktime"] = str(item.commute_commex.all())
            t_result["commute_offtime"] = str(item.commex_date)
            t_result["commute_status"] = item.commex_result
            result["rows"].append(t_result)
    else:
        result = { "total":0, "rows": []}
    return HttpResponse(
        json.dumps(result,ensure_ascii = False),
        content_type="application/json")


@csrf_exempt
def addCommExplain(request):
    attachs = request.FILES
    new_ex_flag = 0
    # upload attach file
    attach_infos = []
    for item in attachs:
        prefix = "commex_" + str(time.time())[0:10]
        path = "./upload/"
        i_attach = {}
        i_attach["commtype"] = item
        i_attach["filename"] = prefix + "_" + attachs[item].name
        i_attach["filetype"] = attachs[item].content_type
        i_attach["filepath"] = path
        file_name = i_attach["filepath"] + i_attach["filename"]
        # upload
        flag, desc = file_upload(attachs[item], path, file_name)
        print desc
        if flag is True:
            logger.info(
                "上传成功(commex_attach_success):{file_name}, {desc}".format(
                file_name=file_name, desc=desc)
            )
        else:
            logger.error(
                "上传失败(commex_attach_fail):{file_name}, {desc}".format(
                file_name=file_name, desc=desc)
            )
        attach_infos.append(i_attach)

    # add attach infos
    for i_attach in attach_infos:
       flag, desc = CommexAttachOb().new(
           attach_minetype = i_attach["filetype"],
           attach_location = i_attach["filepath"],
           attach_filename = i_attach["filename"])
       print desc
       if flag is True:
           logger.info(
               "附件记录成功(attach_info_success):{desc}".format(desc=desc)
           )
       else:
           logger.info(
               "附件记录失败(attach_info_fail):{desc}".format(desc=desc)
           )
    response_data = {}

    id_user = request.user
    realcomm_date = request.POST.get("realcomm_date")
    commex_worktime_reason = request.POST.get("ex_worktime_reason")
    commex_offtime_reason = request.POST.get("ex_offtime_reason")
    commex_worktime_text = request.POST.get("ex_worktime_text")
    commex_offtime_text = request.POST.get("ex_offtime_text")
    if commex_worktime_text:
        commex_worktime_text = "{realcomm_date} {commex_worktime_text}".format(
            realcomm_date = realcomm_date, 
            commex_worktime_text = commex_worktime_text)
    if commex_offtime_text:
        commex_offtime_text = "{realcomm_date} {commex_offtime_text}".format(
            realcomm_date = realcomm_date, 
            commex_offtime_text = commex_offtime_text)
    for i_attach in attach_infos:
        if i_attach["commtype"] == "ex_worktime_upload":
            commex_worktime_attach_filename = i_attach["filename"]
        elif i_attach["commtype"] == "ex_offtime_upload":
            commex_offtime_attach_filename = i_attach["filename"]
    try:
        commex_worktime_attach = CommexAttach.objects.filter(
            comm_attach_filename = commex_worktime_attach_filename)[0]
    except Exception, ex:
        print ex
        commex_worktime_attach = None
    try:
        commex_offtime_attach = CommexAttach.objects.filter(
            comm_attach_filename = commex_offtime_attach_filename)[0]
    except Exception, ex:
        print ex
        commex_offtime_attach = None
    if len(request.POST) > 1:
        # edit comm explain
        try:
            ob_commute_explain = CommuteExplain.objects.get(id_user=request.user, commex_date=realcomm_date)
            print 'already exist'
            flag, desc = CommuteExplainOb().update(
                id_user=request.user,
                commex_date=realcomm_date,
                commex_worktime_reason=commex_worktime_reason,
                commex_offtime_reason=commex_offtime_reason,
                commex_worktime=commex_worktime_text,
                commex_offtime=commex_offtime_text,
                commex_worktime_attach=commex_worktime_attach,
                commex_offtime_attach=commex_offtime_attach)
        # add comm explain
        except Exception, ex:
            flag, desc = CommuteExplainOb().new(
                id_user=request.user,
                commex_date=realcomm_date,
                commex_worktime_reason=commex_worktime_reason,
                commex_offtime_reason=commex_offtime_reason,
                commex_worktime=commex_worktime_text,
                commex_offtime=commex_offtime_text,
                commex_worktime_attach=commex_worktime_attach,
                commex_offtime_attach=commex_offtime_attach)
            print flag, desc
            if flag:
                ob_commute_explain = CommuteExplain.objects.get(id_user=request.user, commex_date=realcomm_date)
                # update xxx
                Commute.objects.filter(id_user=request.user, comm_date=realcomm_date).update(id_commex = ob_commute_explain)
    return HttpResponse(
        json.dumps(response_data), content_type="application/json")

@csrf_exempt
def addCommExplainForm(request):
    today_data = {}
    idate = request.GET["idate"]
    today_data["idate"] = idate
    today_explain = {}
    # commute time
    try:
        icommute = Commute.objects.get(comm_date=idate, id_user=request.user)
        today_data["icommute"] = {
            "worktime": str(icommute.comm_worktime),
            "offtime": str(icommute.comm_offtime)
        }
    except Exception, ex:
        today_data["icommute"] = {}
    # commute explain
    try:
        icommute_explain = CommuteExplain.objects.get(id_user=request.user, commex_date=idate)
        today_explain = icommute_explain
    except Exception, ex:
        print ex
        today_explain = {}
    
    kwvars = {
      'today_data': today_data,
      'today_explain': today_explain
    }
    return render_to_response('workorder/commuteAddExplainForm.html',kwvars)

def delCommExplainFile(request):
    print request.GET
    attach_info = request.GET["file"]
    attach_type = attach_info.split('_')[0]
    attach_id = attach_info.split('_')[1]
    explain_date = attach_info.split('_')[2]
    response_data = {"ret_code":200, "ret_info":""}
    try:
        if attach_type == "worktime":
            CommuteExplain.objects.filter(
                id_user=request.user,
                commex_date=explain_date
            ).update(commex_worktime_attach=None)
            CommexAttach.objects.filter(id_ex_attach=attach_id).delete()
            response_data["ret_info"] = "删除成功"
        elif attach_type == "offtime":
            CommuteExplain.objects.filter(
                id_user=request.user,
                commex_date=explain_date
            ).update(commex_offtime_attach=None)
            response_data["ret_info"] = "删除成功"
            CommexAttach.objects.filter(id_ex_attach=attach_id).delete()
        else:
            response_data["ret_code"] = 400
            response_data["ret_info"] = "数据异常，请联系管理员"
    except Exception, ex:
        print ex
        response_data["ret_code"] = 500
        response_data["ret_info"] = "服务端异常，请联系管理员"
    print response_data
    return HttpResponse(
        json.dumps(response_data), content_type="application/json")
