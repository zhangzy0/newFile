#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from apps.usermanage.views.permission import login_required

from django.db import connection
from django.db.models import Count
from website.common.CommonPaginator import SelfPaginator
from apps.usermanage.views.permission import PermissionVerify, IpaddressAcl
from apps.usermanage.models import User
from apps.workorder.models import Commute, Overtime, CommuteExplain
from apps.workorder.models import IDCList
from apps.workorder.forms import OvertimeForm
from plugins.codegit.date_week_month import getDateWeek
from plugins.codegit.date_week_month import WorkDays
from plugins.codegit.ipy_net import clientIP
import datetime
import calendar
import logging
logger = logging.getLogger('workorder')

@login_required()
@IpaddressAcl()
@PermissionVerify()
def commuteDoit(request):
    form = {}
    form["today"] = datetime.date.today()
    
    if request.method == "POST":
        logger.info(request.POST)
        try:
            commit_type = request.POST["action"]
            try:
                comm_shift = request.POST["shift"]
            except Exception,ex:
                comm_shift = ""
            comm_workip = clientIP(request)
            # prevent repeat submit
            msg = "commit_type:{0}".format(commit_type)
            logger.info(msg)
            if request.session['form_token'] == commit_type:
                raise TypeError
            if commit_type == "worktime" and comm_shift:
                iCommute = Commute(id_user = request.user, comm_worktime = datetime.datetime.today(), 
                                   comm_workip = comm_workip, comm_shift = comm_shift )
                iCommute.save()
                logger.info("{0},{1},{2}".format(request.user, datetime.datetime.today(), comm_workip))
            elif commit_type == "offtime":
                Commute.objects.filter(id_user = request.user,comm_date = datetime.date.today()).update(
                                       comm_offtime = datetime.datetime.today(),comm_offip = comm_workip)
                logger.info("{0},{1},{2}".format(request.user, datetime.datetime.today(), comm_workip))
                iCommute = Commute.objects.get(id_user = request.user,comm_date = datetime.date.today())
                worktime_A = iCommute.comm_date.strftime("%Y-%m-%d") +" 10:00"
                worktime_B = iCommute.comm_date.strftime("%Y-%m-%d") +" 10:30"
                offtime_A = iCommute.comm_date.strftime("%Y-%m-%d") +" 19:00"
                offtime_B = iCommute.comm_date.strftime("%Y-%m-%d") +" 19:30"
                basic_time = {"A":{"worktime":worktime_A,"offtime":offtime_A},
                              "B":{"worktime":worktime_B,"offtime":offtime_B},
                             }
                start_time = iCommute.comm_worktime.strftime("%Y-%m-%d %H:%M")
                end_time = iCommute.comm_offtime.strftime("%Y-%m-%d %H:%M")
                comm_shift = iCommute.comm_shift
                if (start_time < end_time and start_time <= basic_time[comm_shift]["worktime"] 
                    and end_time >= basic_time[comm_shift]["offtime"]):
                    Commute.objects.filter(id_user = request.user, 
                              comm_date = datetime.date.today()).update( comm_status = 1 )
                    logger.info("{0},{1},{2}".format(request.user, datetime.datetime.today(), "正常出勤"))
                else:
                    Commute.objects.filter(id_user = request.user, 
                                           comm_date = datetime.date.today()).update( comm_status = 0 )
                    logger.info("{0},{1},{2}".format(request.user, datetime.datetime.today(), "异常出勤"))
            request.session['form_token'] = commit_type
        except Exception,ex:
            print ex
    else:
        request.session['form_token'] = "hello,world"
    mList = Commute.objects.filter(id_user = request.user).order_by('-comm_date')
    for item in mList:
        print item
        print item.id_commex
    # my commute today 我今天的出勤情况
    try:
        form["mycommute"] = Commute.objects.filter(id_user = request.user,comm_date = datetime.date.today())[0]
    except Exception,ex:
        form["mycommute"] = ""

    form["shift_selected"] = ""
    try:
        myidc = request.user.idc_users.all()[0]
        myidc_users = myidc.id_user.all()
        myidc_users_id = tuple([int(item.id) for item in myidc_users])
        myidc_comm =  Commute.objects.filter(id_user__in = myidc_users_id,comm_date = datetime.date.today())
        for item in myidc_comm:
            form["shift_selected"] = form["shift_selected"]+item.comm_shift
    except Exception,ex:
	print ex
      
    kwvars = {
        'form':form,
        'lPage':mList,
        'request':request,
        'title':'工单系统-上班记录-我的打卡',
        'title_content':'我的打卡',
        'postUrl':'/workorder/commute/doit/',
        'button_type':'add',
    }
    return render_to_response('workorder/commuteDoit.html',kwvars,RequestContext(request))



@login_required()
@IpaddressAcl()
@PermissionVerify()
def commuteList(request):
    form = {}
    mList = Commute.objects.all().order_by('-comm_date')
    logger.info("all user's commute")
    lst = SelfPaginator(request,mList, 15)
    kwvars = {
        'form':form,
        'lPage':lst,
        'request':request,
        'title':'工单系统-上班记录-我的打卡',
        'title_content':'我的打卡',
    }
    return render_to_response('workorder/commuteList.html',kwvars,RequestContext(request))

@login_required()
@IpaddressAcl()
@PermissionVerify()
def overtimeList(request):
    form = {}
    mList = Overtime.objects.filter(id_user = request.user).order_by('-ot_create_time')
    logger.info("all user's overtime list")
    #lst = SelfPaginator(request,mList, 15)
    kwvars = {
        'form':form,
        'lPage':mList,
        'request':request,
        'title':'工单系统-上班记录-加班记录',
        'title_content':'我的加班',
    }
    return render_to_response('workorder/overtimeList.html',kwvars,RequestContext(request))



@login_required()
@IpaddressAcl()
@PermissionVerify()
def overtimeEdit(request,ID):
    iOvertime = Overtime.objects.get(id_overtime=ID)
    logger.info("Edit overtime:{0}".format(ID))
    if request.method == "POST":
        logger.info("request info:{0}".format(request.POST))
        try:
            action = request.POST.get("action")
            ot_from_time = request.POST.get("ot_from_time")
            ot_to_time = request.POST.get("ot_to_time")
            ot_reason = request.POST.get("ot_reason")
            if action == "commit":
                Overtime.objects.filter( id_overtime = iOvertime.id_overtime).update(
                                         ot_status="待审批", ot_from_time = ot_from_time, 
                                         ot_to_time = ot_to_time, ot_reason = ot_reason )
                logger.info("change status to wait approval")
            elif action == "save":
                Overtime.objects.filter( id_overtime = iOvertime.id_overtime).update(
                                         ot_from_time = ot_from_time, ot_to_time = ot_to_time, 
                                         ot_reason = ot_reason )
                logger.info("change status to save")
            return HttpResponseRedirect('/workorder/overtime/list/')
        except Exception,ex:
            logger.error("Exception:{0}".format(ex))
    iOvertime = Overtime.objects.get(id_overtime=ID)
    kwvars = {
        'form':iOvertime,
        'request':request,
        'title':'工单系统-加班申请-编辑加班申请',
        'title_content':'编辑加班申请',
        'postUrl':'/workorder/overtime/edit/{0}/'.format(ID),
        'preUrl':'/workorder/overtime/list/',
        'button_type':'update',
    }
    return render_to_response('workorder/overtimeEdit.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def overtimeAdd(request):
    if request.method == "POST":
        logger.info("request info:{0}".format(request.POST))
        ot_from_time = request.POST.get("ot_from_time")
        ot_to_time = request.POST.get("ot_to_time")
        ot_reason = request.POST.get("ot_reason")
        action = request.POST.get("action")
        if action == "commit":
            ot_status = "待审批"
        elif action == "save":
            ot_status = "待提交"
        ob_Overtime = Overtime( id_user = request.user,\
                                ot_from_time = ot_from_time,\
                                ot_to_time = ot_to_time,\
                                ot_reason = ot_reason,\
                                ot_status = ot_status) 
        logger.info("Overtime Add:{0},{1},{2},{3},{4}".format( 
                     request.user, ot_from_time, ot_to_time, ot_reason, ot_status))
        try:
            ob_Overtime.save()
            logger.info("save success.") 
            return HttpResponseRedirect('/workorder/overtime/list/')
        except Exception,ex:
            logger.error("Exception:{0}".format(ex))
        
    kwvars = {
        'request':request,
        'button_type':'add',
        'title':'工单系统-上班记录-加班申请',
        'title_content':'申请加班',
        'postUrl':'/workorder/overtime/add/',
        'preUrl':'/workorder/overtime/list/',
    }
    return render_to_response('workorder/overtimeAdd.html',kwvars,RequestContext(request))


def overtimeRecordProcess(request,ID):
    logger.info(request.POST)
    action = request.POST.get("action")
    logger.info("action:{0}".format(action))
    ot_record_suggest = request.POST.get("ot_record_suggest")
    #撤销申请 undo 
    if action == "undo":
        Overtime.objects.filter(id_overtime=ID).update(ot_status="待提交")
    # 审批通过
    elif action == "record-ok":
        Overtime.objects.filter(id_overtime=ID).update(ot_status="审批完成",ot_record_result=True, ot_record_suggest=ot_record_suggest,ot_record_user=request.user)
    # 审批不通过
    elif action == "record-fail":
        Overtime.objects.filter(id_overtime=ID).update(ot_status="审批完成",ot_record_result=False,ot_record_suggest=ot_record_suggest,ot_record_user=request.user)
    # 提交
    elif action == "commit":
        Overtime.objects.filter(id_overtime=ID).update(ot_status="待审批")
    else:
        return False


@login_required()
@IpaddressAcl()
@PermissionVerify()
def overtimeView(request,ID):
    iOvertime = Overtime.objects.get(id_overtime=ID)
    logger.info("view overtime :{0}".format(ID))
    if request.method == "POST":
        logger.info(request.POST)
        overtimeRecordProcess(request,ID)
    iOvertime = Overtime.objects.get(id_overtime=ID)
    kwvars = {
        'form':iOvertime,
        'request':request,
        'title':'工单系统-加班申请-加班申请详情',
        'title_content':'加班申请详情',
        'postUrl':'/workorder/overtime/view/{0}/'.format(ID),
        'preUrl':'/workorder/overtime/list/',
    }
    return render_to_response('workorder/overtimeView.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def overtimeRecordView(request,ID):
    iOvertime = Overtime.objects.get(id_overtime=ID)
    logger.info("view overtime record:{0}".format(ID))
    if request.method == "POST":
        logger.info(request.POST)
        overtimeRecordProcess(request,ID)
    iOvertime = Overtime.objects.get(id_overtime=ID)
    kwvars = {
        'form':iOvertime,
        'request':request,
        'title':'工单系统-加班申请-加班申请详情',
        'title_content':'加班申请详情',
        'postUrl':'/workorder/overtime/record/view/{0}/'.format(ID),
        'preUrl':'/workorder/overtime/record/list/',
    }
    return render_to_response('workorder/overtimeView.html',kwvars,RequestContext(request))


@login_required()
@IpaddressAcl()
@PermissionVerify()
def overtimeDel(request,ID):
    Overtime.objects.filter(id_overtime = ID).delete()
    logger.info("view overtime record:{0}".format(ID))
    return HttpResponseRedirect('/workorder/overtime/list/')



@login_required()
@IpaddressAcl()
@PermissionVerify()
def overtimeRecordList(request):
    mList1 = Overtime.objects.filter(ot_status = "待审批" ).order_by('-ot_create_time')
    #lst1 = SelfPaginator(request,mList, 15)
    mList2 = Overtime.objects.filter(ot_status = "审批完成").order_by('-ot_create_time')
    #lst2 = SelfPaginator(request,mList, 15)
    logger.info("view all overtime record")
    kwvars = {
        'lPage1':mList1,
        'lPage2':mList2,
        'request':request,
        'title':'工单系统-上班记录-加班审批单',
        'title_content':'加班审批单',
        'preUrl':'/workorder/overtime/record/list/',
    }
    return render_to_response('workorder/overtimeRecordList.html',kwvars,RequestContext(request))



@login_required()
@IpaddressAcl()
@PermissionVerify()
def commuteCount(request):
    logger.info("all commute count")
    # get all month list
    select = {'month': connection.ops.date_trunc_sql('month', 'comm_date')}
    mouth_obs = Commute.objects.extra(select=select).values('month').annotate(id = Count('comm_date'))
    month_list = [ item["month"].strftime("%Y-%m") for item in mouth_obs ]
    month_list = list(reversed(month_list))
    # get all idc list
    idc_list = IDCList.objects.filter( idc_enable = True )
    all_counter = []
    for month in month_list:
        work_days_ob = WorkDays(month)
        work_days = tuple(work_days_ob.work_days())
        work_days_count = work_days_ob.days_count()
        for idc in idc_list:
            tmp_counter = {'month':month,'idc':idc.idc_cn,'count_ok':0,'count_fail':0,'day_ok':0,'day_fail':0,'normal':work_days_count}
            idcers = idc.id_user.all()
            idcers = [ int(item.id) for item in idcers ]
            count_ok = Commute.objects.filter(comm_status = True, id_user__in = idcers, comm_date__in = work_days).order_by('comm_date')
            count_fail = Commute.objects.filter(comm_status = False, id_user__in = idcers, comm_date__in = work_days).order_by('comm_date')
            if len(idcers) == 1:
                day_ok_sql = """select *,count(id) daysum from ( 
                                        select id_comm,count(id_comm) id 
                                        from workorder_commute 
                                        where comm_status = 1 and id_user_id = {0} and comm_date in {1} group by comm_date i
                                ) as a where id>=2""".format(str(idcers[0]),str(work_days))
                day_fail_sql = """select *,count(id) daysum from ( 
                                        select id_comm,count(id_comm) count_id 
                                        from workorder_commute 
                                        where comm_status = 0 and id_user_id = {0} and comm_date in {1} group by comm_date 
                                  ) as a""".format(str(idcers[0]),str(work_days))
            elif len(idcers) == 0:
                pass
            else :
                day_ok_sql = """select *,count(id) daysum from ( 
                                        select id_comm,count(id_comm) id 
                                        from workorder_commute 
                                        where comm_status = 1 and id_user_id in {0} and comm_date in {1} group by comm_date 
                                ) as a where id>=2""".format(str(tuple(idcers)),str(work_days))
                day_fail_sql = """select *,count(id) daysum from ( 
                                         select id_comm,count(id_comm) id 
                                         from workorder_commute 
                                         where comm_status = 0 and id_user_id in {0} and comm_date in {1} group by comm_date 
                                  ) as a""".format(str(tuple(idcers)),str(work_days))
            day_ok = Commute.objects.raw(day_ok_sql)
            day_fail = Commute.objects.raw(day_fail_sql)
            tmp_counter['count_ok'] = len(count_ok)
            tmp_counter['count_fail'] = len(count_fail)
            try:
                tmp_counter['day_ok'] = day_ok[0].daysum
            except Exception,ex:
                tmp_counter['day_ok'] = 0
            try:
                tmp_counter['day_fail'] = day_fail[0].daysum
            except Exception,ex:
                tmp_counter['day_fail'] = 0
            all_counter.append(tmp_counter)
            
    kwvars = {
        'request':request,
        'title':'工单系统-上班记录-上班统计',
        'title_content':'考勤统计',
        'all_counter':all_counter,
        'preUrl':'/workorder/overtime/record/list/',
    }
    return render_to_response('workorder/commuteCount.html',kwvars,RequestContext(request))



@login_required()
@IpaddressAcl()
@PermissionVerify()
# def explainRecordList(request):
def explainList(request):
    mList = CommuteExplain.objects.filter(id_user = request.user).order_by('-commex_create_time')
    kwvars = {
        'request':request,
        'title':'工单系统-上班记录-上班统计',
        'title_content':'考勤统计',
    }
    return render_to_response('workorder/commuteExplainList.html',kwvars,RequestContext(request))


