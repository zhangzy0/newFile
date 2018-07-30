#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django import forms
from django.contrib import auth
from apps.workorder.models import IDCList,OperList,SpareBrandList,SpareList,ModelList,StatusList,FaultList,DailyInfo,RepairInfo,StockInout,Overtime,Acl,EngineerList,AssetList,AssetModelList
from apps.usermanage.models import User


class IDCListForm(forms.ModelForm):
    class Meta:
        model = IDCList
        exclude = ()
        widgets = {
            'id_idc' : forms.TextInput(attrs={'class':'form-control'}),
            'idc_en' : forms.TextInput(attrs={'class':'form-control'}),
            'idc_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'idc_addr' : forms.TextInput(attrs={'class':'form-control'}),
            'idc_tel' : forms.TextInput(attrs={'class':'form-control'}),
            'idc_qqg' : forms.TextInput(attrs={'class':'form-control'}),
            'idc_enable' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
            #'id_user' : forms.Select(attrs={'class':'form-control'}),
            'id_user' : forms.CheckboxSelectMultiple(choices=[(item.id,item.realname) for item in User.objects.all()]),
        }

    def __init__(self,*args,**kwargs):
        super(IDCListForm,self).__init__(*args,**kwargs)
        self.fields['idc_en'].label=u'机房英文'
        self.fields['idc_en'].error_messages={'required':u'请输入机房英文名称'}
        self.fields['idc_cn'].label=u'机房中文'
        self.fields['idc_cn'].error_messages={'required':u'请输入机房中文名称'}
        self.fields['idc_addr'].label=u'机房地址'
        self.fields['idc_addr'].error_messages={'required':u'请输入机房地址'}
        self.fields['idc_tel'].label=u'联系电话'
        self.fields['idc_tel'].error_messages={'required':u'请输入联系电话'}
        self.fields['idc_qqg'].label=u'QQ群号'
        self.fields['idc_qqg'].error_messages={'required':u'请输入QQ群号'}
        self.fields['idc_enable'].label=u'是否启用'
        self.fields['idc_enable'].error_messages={'required':u'是否启用'}
        self.fields['id_user'].label=u'驻场人员'
        self.fields['id_user'].error_messages={'required':u'请选择驻场人员'}

class OperListForm(forms.ModelForm):
    op_pid = forms.ModelChoiceField(label=u'上级操作',queryset=OperList.objects.all(),empty_label="一级操作",
    widget=forms.Select(attrs={'class':'form-control'})                                
    )
    class Meta:
        model = OperList
        exclude = ()
        widgets = {
            'id_oper' : forms.TextInput(attrs={'class':'form-control'}),
            'op_en' : forms.TextInput(attrs={'class':'form-control'}),
            'op_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'op_descript' : forms.Textarea(attrs={'class':'form-control'}),
            'op_enable' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(OperListForm,self).__init__(*args,**kwargs)
        self.fields['op_en'].label=u'操作英文'
        self.fields['op_en'].error_messages={'required':u'请输入操作英文名称'}
        self.fields['op_cn'].label=u'操作中文'
        self.fields['op_cn'].error_messages={'required':u'请输入操作中文名称'}
        self.fields['op_descript'].label=u'操作描述'
        self.fields['op_descript'].error_messages={'required':u'请输入操作描述信息'}
        #self.fields['op_pid'].label=u'上级操作'
        self.fields['op_pid'].required = False
        #self.fields['op_pid'].error_messages={'required':u'请选择上级操作'}
        self.fields['op_enable'].label=u'是否启用'
        self.fields['op_enable'].error_messages={'required':u'是否启用'}
        
    def clean_op_pid(self):
        if self.cleaned_data.get('op_pid') is None:
            return 0
        elif not self.cleaned_data.get('op_pid').id_op:
            return 0
        return self.cleaned_data.get('op_pid').id_op

class SpareBrandListForm(forms.ModelForm):
    class Meta:
        model = SpareBrandList 
        exclude = ()
        widgets = {
            'id_brand' : forms.TextInput(attrs={'class':'form-control'}),
            'brand_en' : forms.TextInput(attrs={'class':'form-control'}),
            'brand_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'brand_enable' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(SpareBrandListForm,self).__init__(*args,**kwargs)
        self.fields['brand_en'].label=u'厂商英文'
        self.fields['brand_en'].error_messages={'required':u'请输入厂商英文名称'}
        self.fields['brand_cn'].label=u'厂商中文'
        self.fields['brand_cn'].error_messages={'required':u'请输入厂商中文名称'}
        self.fields['brand_enable'].label=u'是否启用'
        self.fields['brand_enable'].error_messages={'required':u'是否启用'}

class SpareListForm(forms.ModelForm):
    class Meta:
        model = SpareList
        exclude = ()
        widgets = {
            'spare_en' : forms.TextInput(attrs={'class':'form-control'}),
            'spare_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'id_brand' : forms.Select(attrs={'class':'form-control'}),
            'spare_enable' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(SpareListForm,self).__init__(*args,**kwargs)
        self.fields['spare_en'].label=u'备件英文'
        self.fields['spare_en'].error_messages={'required':u'请输入备件英文名称'}
        self.fields['spare_cn'].label=u'备件中文'
        self.fields['spare_cn'].error_messages={'required':u'请输入备件中文名称'}
        self.fields['id_brand'].label=u'所属厂商'
        self.fields['id_brand'].error_messages={'required':u'请输入中文名称'}
        self.fields['spare_enable'].label=u'是否启用'
        self.fields['spare_enable'].error_messages={'required':u'是否启用'}


class ModelListForm(forms.ModelForm):
    class Meta:
        model = ModelList
        exclude = ()
        widgets = {
            'id_model' : forms.Select(attrs={'class':'form-control'}),
            'model_en' : forms.TextInput(attrs={'class':'form-control'}),
            'model_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'id_brand' : forms.Select(attrs={'class':'form-control'}),
            'model_enable' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(ModelListForm,self).__init__(*args,**kwargs)
        self.fields['model_en'].label=u'机型英文'
        self.fields['model_en'].error_messages={'required':u'请输入机型英文名称'}
        self.fields['model_cn'].label=u'机型中文'
        self.fields['model_cn'].error_messages={'required':u'请输入机型中文名称'}
        self.fields['model_enable'].label=u'是否启用'
        self.fields['model_enable'].error_messages={'required':u'是否启用'}
        self.fields['id_brand'].label=u'机型厂商'
        self.fields['id_brand'].error_messages={'required':u'请选择机型厂商'}
        self.fields['id_brand'].required = True


class EngineerListForm(forms.ModelForm):
    class Meta:
        model = EngineerList
        exclude = ()
        widgets = {
            'id_engineer' : forms.Select(attrs={'class':'form-control'}),
            'engineer_en': forms.TextInput(attrs={'class': 'form-control'}),
            'engineer_cn': forms.TextInput(attrs={'class': 'form-control'}),
            'engineer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'engineer_ID': forms.TextInput(attrs={'class': 'form-control'}),
            'engineer_zone': forms.Select(choices=(('BJ', u'北京'), ('GD', u'广东'),('NM',u'内蒙'),('SC',u'四川'),('JS',u'江苏')),attrs={'class': 'form-control'}),
            'id_brand': forms.Select(attrs={'class': 'form-control'}),
            'engineer_enable': forms.Select(choices=((True, u'启用'), (False, u'禁用')),attrs={'class': 'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(EngineerListForm,self).__init__(*args,**kwargs)
        self.fields['engineer_en'].label=u'工程师英文'
        self.fields['engineer_en'].error_messages={'required':u'请输入工程师英文名称'}
        self.fields['engineer_cn'].label=u'工程师中文'
        self.fields['engineer_cn'].error_messages={'required':u'请输入工程师中文名称'}
        self.fields['engineer_phone'].label = u'工程师电话'
        self.fields['engineer_phone'].error_messages = {'required': u'请输入工程师电话'}
        self.fields['engineer_ID'].label = u'工程师身份证'
        self.fields['engineer_ID'].error_messages = {'required': u'请输入工程师身份证'}
        self.fields['engineer_zone'].label = u'工程师负责区域'
        self.fields['engineer_zone'].error_messages = {'required': u'请选择工程师负责区域'}
        self.fields['engineer_enable'].label=u'是否启用'
        self.fields['engineer_enable'].error_messages={'required':u'是否启用'}
        self.fields['id_brand'].label=u'工程师厂商'
        self.fields['id_brand'].error_messages={'required':u'请选择工程师厂商'}
        self.fields['id_brand'].required = True


class AssetModelListForm(forms.ModelForm):
    class Meta:
        model = AssetModelList
        exclude = ()
        widgets = {
            'id_assetmodel' : forms.Select(attrs={'class':'form-control'}),
            'id_assetbrand': forms.Select(attrs={'class': 'form-control'}),
            'assetmodel_en': forms.TextInput(attrs={'class': 'form-control'}),
            'assetmodel_cn': forms.TextInput(attrs={'class': 'form-control'}),

            'assetmodel_enable': forms.Select(choices=((True, u'启用'), (False, u'禁用')),attrs={'class': 'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(AssetModelListForm,self).__init__(*args,**kwargs)
        self.fields['id_assetbrand'].label = u'资产类型厂商'
        self.fields['id_assetbrand'].error_messages = {'required': u'请选择资产类型'}
        self.fields['id_assetbrand'].required = True
        self.fields['assetmodel_en'].label=u'资产类型英文'
        self.fields['assetmodel_en'].error_messages={'required':u'请输入资产类型英文名称'}
        self.fields['assetmodel_cn'].label=u'资产类型中文'
        self.fields['assetmodel_cn'].error_messages={'required':u'请输入资产类型中文名称'}
        self.fields['assetmodel_enable'].label=u'是否启用'
        self.fields['assetmodel_enable'].error_messages={'required':u'是否启用'}



class StatusListForm(forms.ModelForm):
    class Meta:
        model = StatusList
        exclude = ()
        widgets = {
            'id_st' : forms.Select(attrs={'class':'form-control'}),
            'st_en' : forms.TextInput(attrs={'class':'form-control'}),
            'st_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'st_enable' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(StatusListForm,self).__init__(*args,**kwargs)
        self.fields['st_en'].label=u'工单状态英文'
        self.fields['st_en'].error_messages={'required':u'请输入工单状态英文名称'}
        self.fields['st_cn'].label=u'工单状态中文'
        self.fields['st_cn'].error_messages={'required':u'请输入工单状态中文名称'}
        self.fields['st_enable'].label=u'是否启用'
        self.fields['st_enable'].error_messages={'required':u'是否启用'}

class FaultListForm(forms.ModelForm):
    class Meta:
        model = FaultList
        exclude = ()
        widgets = {
            'id_fault' : forms.Select(attrs={'class':'form-control'}),
            'fault_en' : forms.TextInput(attrs={'class':'form-control'}),
            'fault_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'fault_enable' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(FaultListForm,self).__init__(*args,**kwargs)
        self.fields['fault_en'].label=u'故障类型英文'
        self.fields['fault_en'].error_messages={'required':u'请输入故障类型英文名称'}
        self.fields['fault_cn'].label=u'故障类型中文'
        self.fields['fault_cn'].error_messages={'required':u'请输入故障类型中文名称'}
        self.fields['fault_enable'].label=u'是否启用'
        self.fields['fault_enable'].error_messages={'required':u'是否启用'}

class DailyInfoEditForm(forms.ModelForm):
    class Meta:
        model = DailyInfo
        fields = ('dainfo_code','id_user','id_st','id_idc','id_op','id_op_li','dainfo_affirm','dainfo_content')
        widgets = {
            'id_idc' : forms.Select(attrs={'class':'form-control'}),
            'id_op' : forms.Select(choices=[(x.id_op,x.op_en) for x in OperList.objects.filter(op_pid = '0')],attrs={'class':'form-control'}),
            'id_op_li' : forms.Select(attrs={'class':'form-control'}),
            'dainfo_content' : forms.Textarea(attrs={'class':'form-control ckeditor'}),
            'dainfo_affirm' : forms.RadioSelect(choices=((True,u'确认'),(False,u'不需要确认'))),
            'dainfo_code' : forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
            'id_user' : forms.Select(attrs={'class':'form-control','readonly':'readonly','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
            'id_st' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
        }

    def __init__(self,*args,**kwargs):
        super(DailyInfoEditForm,self).__init__(*args,**kwargs)
        self.fields['dainfo_code'].label=u'工单编号'
        self.fields['id_user'].label=u'创建者'
        self.fields['id_st'].label=u'当前状态'
        self.fields['id_idc'].label=u'服务机房'
        self.fields['id_idc'].error_messages={'required':u'请选择操作机房'}
        self.fields['dainfo_affirm'].label=u'操作前确认'
        self.fields['dainfo_affirm'].error_messages={'required':u'请选择操作前是否确认'}
        self.fields['dainfo_content'].label=u'工单详情'
        self.fields['dainfo_content'].error_messages={'required':u'请输入工单详情'}
        self.fields['id_op'].label=u'操作大类'
        self.fields['id_op'].error_messages={'required':u'请选择操作大类'}
        self.fields['id_op_li'].label=u'操作子类'
        self.fields['id_op_li'].error_messages={'required':u'请选择操作子类'}

#class RepairInfoAddForm(forms.ModelForm):
#    class Meta:
#        model = RepairInfo
#        fields = ('reinfo_code','id_user','id_st','id_idc','re_sn','id_model','re_rock','id_fault','re_content')
#        widgets = {
#            'id_idc' : forms.Select(attrs={'class':'form-control'}),
#            'id_model' : forms.Select(attrs={'class':'form-control'}),
#            'id_fault' : forms.Select(attrs={'class':'form-control'}),
#            're_sn' : forms.TextInput(attrs={'class':'form-control'}),
#            're_rock' : forms.TextInput(attrs={'class':'form-control'}),
#            'reinfo_code' : forms.TextInput(attrs={'class':'form-control','type':'hidden'}),
#            'id_user' : forms.TextInput(attrs={'class':'form-control','type':'hidden'}),
#            'id_st' : forms.TextInput(attrs={'class':'form-control','type':'hidden'}),
#            're_content' : forms.Textarea(attrs={'class':'form-control ckeditor'}),
#        }
#
#    def __init__(self,*args,**kwargs):
#        super(RepairInfoAddForm,self).__init__(*args,**kwargs)
#        self.fields['id_idc'].label=u'服务机房'
#        self.fields['id_idc'].empty_label=u'请选择机房'
#        self.fields['id_idc'].error_messages={'required':u'请选择操作机房'}
#        self.fields['re_sn'].label=u'SN号'
#        self.fields['re_sn'].error_messages={'required':u'请输入SN号'}
#        self.fields['id_model'].label=u'机型'
#        self.fields['id_model'].empty_label=u'请选择机型'
#        self.fields['id_model'].error_messages={'required':u'请选择机型'}
#        self.fields['re_rock'].label=u'机架位'
#        self.fields['re_rock'].error_messages={'required':u'请输入机架位'}
#        self.fields['id_fault'].label=u'故障类型'
#        self.fields['id_fault'].empty_label=u'请选择故障类型'
#        self.fields['id_fault'].error_messages={'required':u'请选择故障类型'}
#        self.fields['re_content'].label=u'工单详情'
#        self.fields['re_content'].error_messages={'required':u'请输入工单详情'}
#
#
#class RepairInfoEditForm(forms.ModelForm):
#    class Meta:
#        model = RepairInfo
#        fields = ('reinfo_code','id_user','id_st','id_idc','re_sn','id_model','re_rock','id_fault','re_content')
#        widgets = {
#            'id_idc' : forms.Select(attrs={'class':'form-control'}),
#            'id_model' : forms.Select(attrs={'class':'form-control'}),
#            'id_fault' : forms.Select(attrs={'class':'form-control'}),
#            're_sn' : forms.TextInput(attrs={'class':'form-control'}),
#            're_rock' : forms.TextInput(attrs={'class':'form-control'}),
#            'reinfo_code' : forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
#            'id_user' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
#            'id_st' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
#            're_content' : forms.Textarea(attrs={'class':'form-control ckeditor'}),
#        }
#
#    def __init__(self,*args,**kwargs):
#        super(RepairInfoEditForm,self).__init__(*args,**kwargs)
#        self.fields['id_idc'].label=u'服务机房'
#        self.fields['id_idc'].error_messages={'required':u'请选择操作机房'}
#        self.fields['re_sn'].label=u'SN号'
#        self.fields['re_sn'].error_messages={'required':u'请输入SN号'}
#        self.fields['id_model'].label=u'机型'
#        self.fields['id_model'].error_messages={'required':u'请选择机型'}
#        self.fields['re_rock'].label=u'机架位'
#        self.fields['re_rock'].error_messages={'required':u'请输入机架位'}
#        self.fields['id_fault'].label=u'故障类型'
#        self.fields['id_fault'].error_messages={'required':u'请选择故障类型'}
#        self.fields['reinfo_code'].label=u'工单号'
#        self.fields['reinfo_code'].error_messages={'required':u'工单号'}
#        self.fields['id_user'].label=u'创建人'
#        self.fields['id_user'].error_messages={'required':u'创建人'}
#        self.fields['id_st'].label=u'工单状态'
#        self.fields['id_st'].error_messages={'required':u'工单状态'}
#        self.fields['re_content'].label=u'工单详情'
#        self.fields['re_content'].error_messages={'required':u'工单详情不能为空'}
#
#
#class RepairInfoViewForm(forms.ModelForm):
#    class Meta:
#        model = RepairInfo
#        fields = ('reinfo_code','id_user','id_st','id_idc','re_sn','id_model','re_rock','id_fault','re_content')
#        widgets = {
#            'id_idc' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
#            're_sn' : forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
#            're_rock' : forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
#            'reinfo_code' : forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
#            'id_user' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
#            'id_st' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
#            'id_fault' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
#            'id_model' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
#            're_content' : forms.Textarea(attrs={'readonly':'readonly','disable':'disable'}),
#        }
#
#    def __init__(self,*args,**kwargs):
#        super(RepairInfoViewForm,self).__init__(*args,**kwargs)
#        self.fields['id_idc'].label=u'服务机房'
#        self.fields['id_idc'].error_messages={'required':u'请选择操作机房'}
#        self.fields['re_sn'].label=u'SN号'
#        self.fields['re_sn'].error_messages={'required':u'请输入SN号'}
#        self.fields['id_model'].label=u'机型'
#        self.fields['id_model'].error_messages={'required':u'请选择机型'}
#        self.fields['re_rock'].label=u'机架位'
#        self.fields['re_rock'].error_messages={'required':u'请输入机架位'}
#        self.fields['id_fault'].label=u'故障类型'
#        self.fields['id_fault'].error_messages={'required':u'请选择故障类型'}
#        self.fields['reinfo_code'].label=u'工单号'
#        self.fields['reinfo_code'].error_messages={'required':u'工单号'}
#        self.fields['id_user'].label=u'创建人'
#        self.fields['id_user'].error_messages={'required':u'创建人'}
#        self.fields['id_st'].label=u'工单状态'
#        self.fields['id_st'].error_messages={'required':u'工单状态'}
#        self.fields['re_content'].label=u'工单详情'
#        self.fields['re_content'].error_messages={'required':u'工单详情不能为空'}

class StockInoutAddForm(forms.ModelForm):
    class Meta:
        model = StockInout
        exclude = ()
        widgets = {
            'id_reinfo' : forms.Select(attrs={'class':'form-control'}),
            'stio_type' : forms.Select(choices=[('','请选择'),('入库','入库'),('报废','报废'),('故障启用备件','故障启用备件'),('厂家返回','厂家返回')],attrs={'class':'form-control'}),
            'id_spare' : forms.Select(attrs={'class':'form-control'}),
            'stio_num' : forms.TextInput(attrs={'class':'form-control'}),
            'stio_descript' : forms.Textarea(attrs={'class':'form-control'}),
            'id_user' : forms.TextInput(attrs={'class':'form-control','type':'hidden'}),
        }

    def __init__(self,*args,**kwargs):
        super(StockInoutAddForm,self).__init__(*args,**kwargs)
        self.fields['id_reinfo'].label=u'报修工单ID'
        self.fields['id_reinfo'].empty_label=u'非工单添加-手动录入'
        self.fields['stio_type'].label=u'出入类型'
        self.fields['stio_type'].error_messages={'required':u'出入类型不能为空'}
        self.fields['id_spare'].label=u'备件类型'
        self.fields['id_spare'].error_messages={'required':u'备件类型'}
        self.fields['stio_num'].label=u'备件数量'
        self.fields['stio_num'].error_messages={'required':u'添加人不能为空'}
        self.fields['stio_descript'].label=u'出入描述'
        self.fields['stio_descript'].error_messages={'required':u'出入描述不能为空'}
        self.fields['id_user'].label=u'添加人'
        #self.fields['id_user'].error_messages={'required':u'添加人不能为空'}


class StockInoutEditForm(forms.ModelForm):
    class Meta:
        model = StockInout
        exclude = ()
        widgets = {
            'id_reinfo' : forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}),
            'stio_type' : forms.TextInput(attrs={'class':'form-control'}),
            'id_spare' : forms.Select(attrs={'class':'form-control'}),
            'stio_num' : forms.TextInput(attrs={'class':'form-control'}),
            'stio_descript' : forms.Textarea(attrs={'class':'form-control'}),
            'id_user' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
        }

    def __init__(self,*args,**kwargs):
        super(StockInoutEditForm,self).__init__(*args,**kwargs)
        self.fields['id_reinfo'].label=u'工单ID'
        self.fields['stio_type'].label=u'出入类型'
        self.fields['stio_type'].error_messages={'required':u'出入类型不能为空'}
        self.fields['id_spare'].label=u'备件类型'
        self.fields['id_spare'].error_messages={'required':u'备件类型'}
        self.fields['stio_num'].label=u'备件数量'
        self.fields['stio_num'].error_messages={'required':u'添加人不能为空'}
        self.fields['stio_descript'].label=u'出入描述'
        self.fields['stio_descript'].error_messages={'required':u'出入描述不能为空'}
        self.fields['id_user'].label=u'添加人'
        self.fields['id_user'].error_messages={'required':u'添加人不能为空'}


class AssetListForm(forms.ModelForm):
    class Meta:
        model = AssetList
        exclude = ['asset_from','asset_to','asset_num','asset_enable']
        widgets = {
            'id_assettype' : forms.Select(attrs={'class':'form-control'}),
            'id_idc' : forms.Select(attrs={'class':'form-control'}),
            'id_assetmodel' : forms.Select(attrs={'class':'form-control'}),
            'id_assetbrand': forms.Select(attrs={'class': 'form-control'}),
            'asset_sn' : forms.TextInput(attrs={'class':'form-control'}),
            'asset_num' : forms.TextInput(attrs={'class':'form-control'}),
            'asset_st' : forms.Select(choices=((1,u'好件'),(2,u'坏件')),attrs={'class':'form-control'}),
            'asset_descript': forms.TextInput(attrs={'class':'form-control'}),
            'id_user' : forms.Select(attrs={'class':'form-control','readonly':'readonly','onfocus':'this.defaultIndex=this.selectedIndex;','onchange':'this.selectedIndex=this.defaultIndex;'}),
        }

    def __init__(self,*args,**kwargs):
        super(AssetListForm,self).__init__(*args,**kwargs)
        self.fields['id_assettype'].label=u'资产类型'
        self.fields['id_assettype'].error_messages={'required':u'资产类型不能为空'}
        self.fields['id_assettype'].required = True
        self.fields['id_idc'].label=u'所属机房'
        self.fields['id_idc'].error_messages={'required':u'所属机房不能为空'}
        self.fields['id_idc'].required = True
        self.fields['id_assetmodel'].label=u'资产型号'
        self.fields['id_assetmodel'].error_messages={'required':u'资产型号不能为空'}
        self.fields['id_assetmodel'].required = True
        self.fields['id_assetbrand'].label = u'资产厂商'
        self.fields['id_assetbrand'].error_messages = {'required': u'资产厂商不能为空'}
        self.fields['id_assetbrand'].required = True
        self.fields['asset_sn'].label=u'序列号'
        self.fields['asset_sn'].error_messages={'required':u'序列号不为空'}
        self.fields['asset_sn'].required = True
        self.fields['asset_st'].label=u'状态'
        self.fields['asset_st'].error_messages={'required':u'状态不能为空'}
        self.fields['asset_descript'].label = u'备注'
        self.fields['asset_descript'].error_messages = {'required': u'备注不能为空'}
        self.fields['id_user'].label = u'添加人'
        self.fields['id_user'].error_messages = {'required': u'添加人不能为空'}


class OvertimeForm(forms.ModelForm):
    class Meta:
        model = Overtime
        fields = ('ot_from_time','ot_to_time','ot_reason')
        widgets = {
            'ot_from_time' : forms.TextInput(attrs={'class':'input-group date form_datetime'}),
            'ot_to_time' : forms.TextInput(attrs={'class':'form-control'}),
            'ot_reason' : forms.Textarea(attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(OvertimeForm,self).__init__(*args,**kwargs)
        self.fields['ot_from_time'].label=u'开始时间'
        self.fields['ot_from_time'].error_messages={'required':u'请选择开始时间'}
        self.fields['ot_to_time'].label=u'结束时间'
        self.fields['ot_to_time'].error_messages={'required':u'请选择结束时间'}
        self.fields['ot_reason'].label=u'加班原因'
        self.fields['ot_reason'].error_messages={'required':u'请输入加班原因'}


class AclForm(forms.ModelForm):
    class Meta:
        model = Acl
        exclude = ()
        widgets = {
            'acl_ip' : forms.TextInput(attrs={'class':'form-control'}),
            'acl_mask' : forms.TextInput(attrs={'class':'form-control'}),
            'id_user' : forms.TextInput(attrs={'class':'form-control','type':'hidden'}),
            'acl_descript' : forms.TextInput(attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(AclForm,self).__init__(*args,**kwargs)
        self.fields['acl_ip'].label=u'IP'
        self.fields['acl_ip'].error_messages={'required':u'请输入IP'}
        self.fields['acl_mask'].label=u'子网'
        self.fields['acl_mask'].error_messages={'required':u'请输入子网'}
        self.fields['acl_descript'].label=u'描述'
        self.fields['acl_descript'].error_messages={'required':u'请输入描述'}
        

