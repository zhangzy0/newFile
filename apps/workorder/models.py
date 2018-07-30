#!/usr/bin/env python
#-*- coding: utf-8 -*-

from apps.usermanage.models import User
from django.db import models
import django.utils.timezone as timezone
import uuid

# Create your models here.
class IDCList(models.Model):
    '''
机房列表
    '''
    id_idc = models.AutoField(primary_key=True)
    idc_en = models.CharField(max_length=64)
    idc_cn = models.CharField(max_length=64)
    idc_addr = models.CharField(max_length=255)
    idc_tel = models.CharField(max_length=11)
    idc_qqg = models.CharField(max_length=15)
    idc_enable = models.BooleanField(default=True)
    id_user = models.ManyToManyField(User,related_name='idc_users',null=True,blank=True)
    #id_user = models.ForeignKey(User,null=True,blank=True)

    def __unicode__(self):
        return '%s' %(self.idc_cn)

class OperList(models.Model):
    '''
操作类型
    '''
    id_op = models.AutoField(primary_key=True)
    op_en = models.CharField(max_length=64)
    op_cn = models.CharField(max_length=64)
    op_enable = models.BooleanField(default=True)
    op_pid = models.IntegerField()
    #op_pid = models.ForeignKey('self',verbose_name="top_oper")
    op_descript = models.CharField(max_length=1024)

    def __unicode__(self):
        return '%s' %(self.op_cn)

class StatusList(models.Model):
    '''
工单状态
    '''
    id_st = models.AutoField(primary_key=True)
    st_en = models.CharField(max_length=64)
    st_cn = models.CharField(max_length=64)
    st_enable = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s' %(self.st_cn)




class SpareBrandList(models.Model):
    '''
备件厂商
    '''
    id_brand = models.AutoField(primary_key=True)
    brand_en = models.CharField(max_length=64)
    brand_cn = models.CharField(max_length=64)
    brand_email = models.EmailField(max_length=255,null=True)
    brand_enable = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s' %(self.brand_cn)


class AssetTypeList(models.Model):
    '''
资产类型列表
    '''
    id_assettype = models.AutoField(primary_key=True)
    assettype_en = models.CharField(max_length=64)
    assettype_cn = models.CharField(max_length=64)
    assettype_enable = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s' %(self.assettype_cn)



class EngineerList(models.Model):
    '''
    厂商工程师名单
    '''
    id_engineer = models.AutoField(primary_key=True)
    engineer_en = models.CharField(max_length=64)
    engineer_cn = models.CharField(max_length=64)
    engineer_zone = models.CharField(max_length=64)
    id_brand = models.ForeignKey(SpareBrandList, null=True, blank=True)
    engineer_phone = models.CharField(max_length=64)
    engineer_ID = models.CharField(max_length=64)
    engineer_enable = models.BooleanField(default=True)
    def __unicode__(self):
        return '%s %s' %(self.id_brand.brand_en,self.engineer_en)


class ModelList(models.Model):
    '''
机器型号
    '''
    id_model = models.AutoField(primary_key=True)
    model_en = models.CharField(max_length=64)
    model_cn = models.CharField(max_length=64)
    id_brand = models.ForeignKey(SpareBrandList,null=True,blank=True)
    model_enable = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s %s' %(self.id_brand.brand_en,self.model_en)


class FaultTypeList(models.Model):
    '''
    故障分类
    '''
    id_faulttype = models.AutoField(primary_key=True)
    faulttype_en = models.CharField(max_length=64)
    faulttype_cn = models.CharField(max_length=64)
    faulttype_enable = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s' %(self.faulttype_cn)

class FaultList(models.Model):
    '''
故障类型
    '''
    id_fault = models.AutoField(primary_key=True)
    fault_en = models.CharField(max_length=64)
    fault_cn = models.CharField(max_length=64)
    fault_enable = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s' %(self.fault_cn)


class SpareList(models.Model):
    '''
备件类型
    '''
    id_spare = models.AutoField(primary_key=True)
    spare_en = models.CharField(max_length=64)
    spare_cn = models.CharField(max_length=64)
    id_brand = models.ForeignKey(SpareBrandList,null=True,blank=True)
    spare_enable = models.BooleanField(default=True)

    def __unicode__(self):
        #return '%s %s' %(self.id_brand.brand_en,self.spare_en)
        return '%s %s' %(self.id_brand.brand_en,self.spare_en)


class AssetModelList(models.Model):
    '''
资产类型列表
    '''
    id_assetmodel = models.AutoField(primary_key=True)
    assetmodel_en = models.CharField(max_length=64)
    assetmodel_cn = models.CharField(max_length=64)
    id_assetbrand = models.ForeignKey(SpareBrandList,null=True,blank=True)
    assetmodel_enable = models.BooleanField(default=True)

    def __unicode__(self):
        return self.assetmodel_en


class Acl(models.Model):
    '''
登录限制
    '''
    id_acl = models.AutoField(primary_key=True)
    acl_ip = models.GenericIPAddressField()
    acl_mask = models.IntegerField()
    acl_descript = models.CharField(max_length=1024)
    acl_create_time = models.DateTimeField(auto_now_add=True) 
    id_user = models.ForeignKey(User,null=True,blank=True)
    
    def __unicode__(self):
        return '%s(%s)' %(self.acl_ip,self.acl_mask)


class Syslog(models.Model):
    '''
系统日志
    '''
    id_log = models.AutoField(primary_key=True)
    log_type = models.CharField(max_length=64)
    id_user = models.ForeignKey(User,null=True,blank=True)
    log_content = models.TextField()
    log_opertime = models.DateTimeField(auto_now_add=True)
    log_ip = models.GenericIPAddressField()

#class MultDailyInfo(models.Model):
#    '''
#Mult日常工单
#    '''
#    id_mult_dainfo = models.AutoField(primary_key=True)
#    mult_dainfo_code = models.CharField(max_length=64)
#    id_idc = models.ForeignKey(IDCList,null=True,blank=True)
#    id_user = models.ForeignKey(User,null=True,blank=True)
#    mult_dainfo_create_time = models.DateTimeField(auto_now_add=True)
#    id_op = models.ForeignKey(OperList,related_name='mult_dailyinfo_op',null=True,blank=True)
#    id_op_li = models.ForeignKey(OperList,related_name='mult_dailyinfo_op_li',null=True,blank=True)
#    id_st = models.ForeignKey(StatusList,null=True,blank=True)
#    mult_dainfo_num = models.IntegerField(null=True,default=1,blank=True)
#    mult_dainfo_affirm = models.CharField(max_length=64)
#    mult_dainfo_content = models.TextField()


class DailyInfo(models.Model):
    '''
日常工单
    '''
    id_dainfo = models.AutoField(primary_key=True)
    dainfo_code = models.CharField(max_length=64)
    id_idc = models.ForeignKey(IDCList,null=True,blank=True)
    id_model = models.ForeignKey(ModelList,null=True,blank=False)
    dainfo_sn = models.CharField(max_length=64,null=True, blank = False)
    dainfo_rock = models.CharField(max_length=64,null=True, blank = False)
    id_user = models.ForeignKey(User,null=True,blank=True)
    dainfo_create_time = models.DateTimeField(auto_now_add=True)
    id_op = models.ForeignKey(OperList,related_name='dailyinfo_op',null=True,blank=True)
    id_op_li = models.ForeignKey(OperList,related_name='dailyinfo_op_li',null=True,blank=True)
    id_st = models.ForeignKey(StatusList,null=True,blank=True)
    dainfo_affirm = models.CharField(max_length=64)
    dainfo_content = models.TextField()
    def __unicode__(self):
        return '%s' %(self.dainfo_code)

class DailyInfoFault(models.Model):
    '''
日常工单的故障描述
    '''
    id_dafault = models.AutoField(primary_key=True)
    id_dainfo = models.ForeignKey(DailyInfo)
    id_fault = models.ForeignKey(FaultList,null=True,blank=True)
    dafault_desc = models.CharField(max_length=512)

class RepairInfo(models.Model):
    '''
报修工单
    '''
    id_reinfo = models.AutoField(primary_key=True)
    reinfo_code = models.CharField(max_length=64)
    id_idc = models.ForeignKey(IDCList,null=True,blank=False)
    id_user = models.ForeignKey(User,null=True,blank=True)
    re_content = models.TextField()
    re_create_time = models.DateTimeField(auto_now_add=True)
    roc_start_time = models.DateTimeField(null=True, blank=True)
    id_model = models.ForeignKey(ModelList,null=True,blank=False)
    id_faulttype = models.ForeignKey(FaultTypeList,null=True,blank=True)
    re_sn = models.CharField(max_length=64, blank = False)
    #re_mt = models.CharField(max_length=64, blank = False)
    re_rock = models.CharField(max_length=64, blank = False)
    id_st = models.ForeignKey(StatusList,null = True, blank = True)   #工单的状态
    re_come_time = models.DateTimeField(null = True, blank = True)
    re_submitted = models.BooleanField(default = False)
    def __unicode__(self):
        return '%s' %(self.reinfo_code)

class StockList(models.Model):
    '''
硬盘库存表
    '''
    id_stock = models.AutoField(primary_key=True)
    #id_idc = models.ForeignKey(IDCList,null=True,blank=True)
    id_spare = models.ForeignKey(SpareList,null=True,blank=True)
    stock_area = models.CharField(max_length=64)
    stock_sn = models.CharField(max_length=64, unique=True)
    stock_st = models.IntegerField(null=True,blank=True)
    stock_from = models.DateTimeField(null=True,blank=True)
    stock_to = models.DateTimeField(null=True,blank=True)
    def __unicode__(self):
        return '%s' %(self.stock_sn)


class AssetList(models.Model):
    '''
资产库存表
    '''
    id_asset = models.AutoField(primary_key=True,verbose_name='序号')
    id_idc = models.ForeignKey(IDCList,null=True,blank=True,verbose_name='机房')
    id_assettype = models.ForeignKey(AssetTypeList,null=True,blank=True,verbose_name='类型')
    id_assetmodel = models.ForeignKey(AssetModelList,null=True,blank=True,verbose_name='型号')
    id_assetbrand = models.ForeignKey(SpareBrandList, null=True, blank=True,verbose_name='厂商')
    asset_sn = models.CharField(max_length=64, unique=True,verbose_name='SN')
    asset_num = models.IntegerField(null=True,blank=True,verbose_name='数量')
    asset_st = models.IntegerField(null=True,blank=True,verbose_name='状态')
    asset_from = models.DateTimeField(null=True,blank=True)
    asset_to = models.DateTimeField(null=True,blank=True)
    asset_descript = models.CharField(max_length=1024,null=True, blank=True,verbose_name='备注')
    id_user = models.ForeignKey(User, null=True, blank=True,verbose_name='添加人')
    asset_enable = models.BooleanField(default=True)
    asset_create_time = models.DateTimeField(auto_now_add=True,verbose_name='添加时间')
    def __unicode__(self):
        return '%s' %(self.asset_sn)


class AssetInout(models.Model):
    '''
资产操作记录
    '''
    id_asinout = models.AutoField(primary_key=True)
    id_assettype = models.ForeignKey(AssetTypeList,null=True,blank=True)
    id_idc = models.ForeignKey(IDCList, null=True, blank=True)
    id_assetmodel = models.ForeignKey(AssetModelList,null=True,blank=True)
    id_assetbrand = models.ForeignKey(SpareBrandList, null=True, blank=True)
    asio_type = models.CharField(max_length=64)
    asio_num = models.IntegerField()
    asio_descript = models.CharField(max_length=1024,null=True, blank=True)
    id_assetlist = models.ManyToManyField(AssetList, related_name='log_asset', null=True, blank=True)
    asio_create_time = models.CharField(max_length=64)
    id_user = models.ForeignKey(User,null=True,blank=True)




class RepairInfoFault(models.Model):
    '''
    报修工单的故障类型
    '''
    id_refault = models.AutoField(primary_key=True)
    id_reinfo = models.ForeignKey(RepairInfo)
    id_spare = models.ForeignKey(SpareList,null=True,blank=True)
    id_fault = models.ForeignKey(FaultList,null=True,blank=True)
    refault_num = models.IntegerField(null=True,blank=True,default=1)
    refault_desc = models.CharField(max_length=512)
    refault_slot = models.CharField(max_length=64, blank = True, default = "")
    refault_status = models.NullBooleanField(null = True, default = True)
    refault_spare_producer = models.CharField(max_length=64,null = True, default = "")
    refault_spare_sn = models.CharField(max_length=64,null = True, default = "")
    #refault_spare_sn_new = models.CharField(max_length=64, null = True, default = "")
    refault_spare_sn_new = models.ForeignKey(StockList,null=True,blank=True)
    def __unicode__(self):
        return '%s' %(self.stock_sn)


class SpareLack(models.Model):
    '''
    缺少的备件
    '''
    id_refault = models.AutoField(primary_key=True)
    id_reinfo = models.ForeignKey(RepairInfo,verbose_name=u"工单的id号",null=True,blank=True,)
    # id_fault = models.ForeignKey(FaultList,null=True,blank=True,verbose_name=u"缺少备件的类型类型")
    fault = models.CharField(max_length=50,null=True, blank=True, verbose_name=u"缺少备件的类型类型")
    refault_desc = models.CharField(max_length=512,null=True,blank=True,verbose_name=u"备注描述")
    id_user = models.ForeignKey(User, null=True, blank=True,verbose_name=u"提交者")
    id_st = models.ForeignKey(StatusList, null=True, blank=True, verbose_name=u"工单状态")
    add_time = models.DateTimeField(auto_now_add=True,null=True, blank=True,verbose_name=u"提交时间")


class Process(models.Model):
    '''
工单流程
    '''
    id_proc = models.AutoField(primary_key=True)
    pr_wocode = models.CharField(max_length=30)
    # pr_start_time = models.DateTimeField(auto_now_add=True)
    # pr_end_time = models.DateTimeField(auto_now=True)
    pr_start_time = models.DateTimeField(default=timezone.now)
    pr_end_time = models.DateTimeField(default=timezone.now)
    id_user = models.ForeignKey(User,null=True,blank=True)
    id_st = models.ForeignKey(StatusList,null=True,blank=True)
    id_engi = models.ForeignKey(EngineerList,null=True,blank=True)
    pr_spare = models.CharField(max_length=100, null=True, blank=True)

class Remark(models.Model):
    '''
工单备注
    '''
    id_remark = models.AutoField(primary_key=True)
    re_wocode = models.CharField(max_length=30)
    mark_content = models.TextField()
    id_user = models.ForeignKey(User,null=True,blank=True)
    mark_time = models.DateTimeField(auto_now_add=True)

class DailywoAttach(models.Model):
    '''
附件
    '''
    id_attach = models.AutoField(primary_key=True)
    id_dainfo = models.ForeignKey(DailyInfo,null=True,blank=True)
    attach_minetype = models.CharField(max_length=500,blank=True)
    attach_location = models.FileField(upload_to='./uploads/')
    attach_filename = models.CharField(max_length=256)
    attach_downloadnum = models.IntegerField(null=True,default=0)
    attach_create_time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return '{id_attach}'.format(self.id_attach)



#ch_stio_type=(("入库","入库"),("替换","替换"))
class StockInout(models.Model):
    '''
备件操作记录
    '''
    id_stinout = models.AutoField(primary_key=True)
    id_reinfo = models.ForeignKey(RepairInfo,null=True,blank=True)
    #stio_type = models.CharField(max_length=64,choices=ch_stio_type,null=False)
    stio_type = models.CharField(max_length=64)
    id_spare = models.ForeignKey(SpareList,null=True,blank=True)
    stio_num = models.IntegerField()
    stio_descript = models.CharField(max_length=1024)
    id_stock = models.ManyToManyField(StockList, related_name='log_stock',null=True,blank=True)
    #models.ManyToManyField(User,related_name='idc_users',null=True,blank=True)
    stio_create_time = models.DateTimeField(auto_now_add=True) 
    id_user = models.ForeignKey(User,null=True,blank=True)





class CommexAttach(models.Model):
    '''
考勤解释附件
    '''
    id_ex_attach = models.AutoField(primary_key=True)
    comm_attach_minetype = models.CharField(max_length=500,blank=True)
    comm_attach_location = models.FileField(upload_to='./uploads/')
    comm_attach_filename = models.CharField(max_length=256,default=None)
    comm_attach_downloadnum = models.IntegerField(null=True,default=0)
    comm_attach_create_time = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return '{id_attach}'.format(id_attach = self.id_ex_attach)
    

class CommuteExplain(models.Model):
    '''
考勤解释
    '''
    id_commex = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User,related_name='commex_create_user',null=True)
    commex_date = models.DateField(null=False)
    commex_worktime = models.DateTimeField(null=True)
    commex_offtime = models.DateTimeField(null=True)
    commex_worktime_reason = models.CharField(max_length=1024,null=True)
    commex_offtime_reason = models.CharField(max_length=1024,null=True)
    commex_worktime_attach = models.ForeignKey(
        CommexAttach, related_name='commex_worktime_attach', null=True)
    commex_offtime_attach = models.ForeignKey(
        CommexAttach, related_name='commex_offtime_attach', null=True)
    commex_status = models.CharField(max_length=1024,null=True)
    commex_suggest = models.CharField(max_length=1024,null=True)
    commex_result = models.NullBooleanField(null=True,default=False)
    commex_record_user = models.ForeignKey(User,related_name='commex_record_user',null=True)
    commex_create_time = models.DateTimeField(auto_now_add=True)
    commex_record_time = models.DateTimeField(auto_now=True)


class Commute(models.Model):
    '''
打卡
    '''
    id_comm = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User,null=True,blank=True)
    comm_shift = models.CharField(max_length=1,null=True,blank=True)
    comm_worktime = models.DateTimeField(null=True)
    comm_workip = models.GenericIPAddressField(null=True)
    comm_offtime = models.DateTimeField(null=True)
    comm_offip = models.GenericIPAddressField(null=True)
    comm_date = models.DateField(auto_now=True)
    comm_status = models.BooleanField(default=False)
    comm_note = models.CharField(max_length=1024,null=True)
    id_commex = models.ForeignKey(CommuteExplain,related_name='commute_commex',null=True,blank=True)

class Overtime(models.Model):
    '''
加班记录表
    '''
    id_overtime = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User,related_name='overtime_create_user',null=True,blank=True)
    ot_from_time = models.DateTimeField(null=True)
    ot_to_time = models.DateTimeField(null=True)
    ot_create_time = models.DateTimeField(auto_now_add=True)
    ot_reason = models.CharField(max_length=1024,null=False)
    ot_status = models.CharField(max_length=1024,null=False)
    ot_record_user = models.ForeignKey(User,related_name='overtime_record_user',null=True,blank=True)
    ot_record_time = models.DateTimeField(auto_now=True)
    ot_record_suggest = models.CharField(max_length=1024,null=True)
    ot_record_result = models.NullBooleanField(null=True,default=False)
