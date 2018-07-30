#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django import forms
from django.contrib import auth
#from django.contrib.auth import get_user_model
from apps.usermanage.models import User,RoleList,PermissionList
from django.utils.functional import lazy


class LoginUserForm(forms.Form):
    username = forms.CharField(label=u'账 号',error_messages={'required':u'账号不能为空'},
        widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(label=u'密 码',error_messages={'required':u'密码不能为空'},
        widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        #self.user_cache = None
        self.user_cache = request.user

        super(LoginUserForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = auth.authenticate(username=username,password=password)
            if self.user_cache is None:
                raise forms.ValidationError(u'账号密码不匹配')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(u'此账号已被禁用')
        return self.cleaned_data

    def get_user(self):
        return self.user_cache

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label=u'原始密码',error_messages={'required':'请输入原始密码'},
        widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password1 = forms.CharField(label=u'新密码',error_messages={'required':'请输入新密码'},
        widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password2 = forms.CharField(label=u'重复输入',error_messages={'required':'请重复新输入密码'},
        widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(u'原密码错误')
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if len(password1)<6:
            raise forms.ValidationError(u'密码必须大于6位')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次密码输入不一致')
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

class AddUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','u_mphone','password','email','realname','role','is_active')
        widgets = {
            'username' : forms.TextInput(attrs={'class':'form-control'}),
            'password' : forms.PasswordInput(attrs={'class':'form-control'}),
            'email' : forms.TextInput(attrs={'class':'form-control'}),
            'realname' : forms.TextInput(attrs={'class':'form-control'}),
            'u_mphone' : forms.TextInput(attrs={'class':'form-control'}),
            #'sex' : forms.RadioSelect(choices=((u'男', u'男'),(u'女', u'女')),attrs={'class':'list-inline'}),
            'role' : forms.Select(attrs={'class':'form-control'}),
            'is_active' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(AddUserForm,self).__init__(*args,**kwargs)
        self.fields['username'].label=u'账 号'
        self.fields['username'].error_messages={'required':u'请输入账号'}
        self.fields['password'].label=u'密 码'
        self.fields['password'].error_messages={'required':u'请输入密码'}
        self.fields['email'].label=u'邮 箱'
        self.fields['email'].error_messages={'required':u'请输入邮箱','invalid':u'请输入有效邮箱'}
        self.fields['realname'].label=u'姓 名'
        self.fields['realname'].error_messages={'required':u'请输入姓名'}
        self.fields['u_mphone'].label=u'手 机'
        self.fields['u_mphone'].error_messages={'required':u'请输入手机号码'}
        self.fields['role'].label=u'角 色'
        self.fields['is_active'].label=u'状 态'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError(u'密码必须大于6位')
        return password

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email','realname','u_mphone','role','is_active')
        widgets = {
            'username' : forms.TextInput(attrs={'class':'form-control'}),
            #'password': forms.HiddenInput,
            'email' : forms.TextInput(attrs={'class':'form-control'}),
            'realname' : forms.TextInput(attrs={'class':'form-control'}),
            'u_mphone' : forms.TextInput(attrs={'class':'form-control'}),
            #'sex' : forms.RadioSelect(choices=((u'男', u'男'),(u'女', u'女')),attrs={'class':'list-inline'}),
            'role' : forms.Select(choices=[(x.role_cn,x.role_en) for x in RoleList.objects.all()],attrs={'class':'form-control'}),
            'is_active' : forms.Select(choices=((True, u'启用'),(False, u'禁用')),attrs={'class':'form-control'}),
        }

    def __init__(self,*args,**kwargs):
        super(EditUserForm,self).__init__(*args,**kwargs)
        self.fields['username'].label=u'账 号'
        self.fields['username'].error_messages={'required':u'请输入账号'}
        self.fields['email'].label=u'邮 箱'
        self.fields['email'].error_messages={'required':u'请输入邮箱','invalid':u'请输入有效邮箱'}
        self.fields['realname'].label=u'姓 名'
        self.fields['realname'].error_messages={'required':u'请输入姓名'}
        self.fields['role'].label=u'角 色'
        self.fields['is_active'].label=u'状 态'
        self.fields['u_mphone'].label=u'手 机'
        self.fields['u_mphone'].error_messages={'required':u'请输入手机号码'}

    def clean_password(self):
        return self.cleaned_data['password']


class PermissionListForm(forms.ModelForm):
    per_pid = forms.ModelChoiceField(label=u'上级菜单' ,queryset=PermissionList.objects.all(),empty_label="一级菜单",
        widget=forms.Select(attrs={'class':'form-control'})
    )
    class Meta:
        model = PermissionList
        exclude = ()
        widgets = {
            'per_icon' : forms.TextInput(attrs={'class':'form-control'}),
            'per_en' : forms.TextInput(attrs={'class':'form-control'}),
            'per_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'per_url' : forms.TextInput(attrs={'class':'form-control'}),
            'per_level' : forms.TextInput(attrs={'class':'form-control'}),
            'per_guid' : forms.TextInput(attrs={'class':'form-control'}),
            'id_app' : forms.Select(attrs={'class':'form-control'}),
        }


    def __init__(self,*args,**kwargs):
        super(PermissionListForm,self).__init__(*args,**kwargs)
        self.fields['per_en'].label=u'英文名称'
        self.fields['per_en'].error_messages={'required':u'请输入英文名称'}
        self.fields['per_cn'].label=u'中文名称'
        self.fields['per_cn'].error_messages={'required':u'请输入中文名称'}
        self.fields['per_icon'].label=u'图标icon'
        self.fields['per_icon'].error_messages={'required':u'请选择图标'}
        self.fields['per_url'].label=u'链接地址'
        self.fields['per_url'].error_messages={'required':u'请输入URL'}
        #self.fields['per_pid'].label=u'上级菜单'
        #self.fields['per_pid'].error_messages={'required':u'请选择上级菜单'}
        self.fields['per_pid'].required = False
        self.fields['per_level'].label=u'顺序'
        self.fields['per_level'].error_messages={'required':u'请输入顺序'}
        self.fields['per_guid'].label=u'导航菜单'
        self.fields['id_app'].label=u'站点'
        self.fields['id_app'].error_messages={'required':u'请选择站点'}
    def clean_per_pid(self):
        if self.cleaned_data.get('per_pid') is None:
            return 0
        elif not self.cleaned_data.get('per_pid').id_perm:
            return 0
        return self.cleaned_data.get('per_pid').id_perm

class RoleListForm(forms.ModelForm):
    class Meta:
        model = RoleList
        exclude = ()
        widgets = {
            'role_en' : forms.TextInput(attrs={'class':'form-control'}),
            'role_cn' : forms.TextInput(attrs={'class':'form-control'}),
            'id_perm' : forms.SelectMultiple(attrs={'class':'form-control','size':'10','multiple':'multiple'}),
            #'id_perm' : forms.CheckboxSelectMultiple(choices=[(x.id_perm,x.per_cn) for x in PermissionList.objects.all()]),
        }

    def __init__(self,*args,**kwargs):
        super(RoleListForm,self).__init__(*args,**kwargs)
        self.fields['role_en'].label=u'名称英文'
        self.fields['role_en'].error_messages={'required':u'请输入名称英文'}
        self.fields['role_cn'].label=u'名称中文'
        self.fields['role_cn'].error_messages={'required':u'请输入名称中文'}
        self.fields['id_perm'].label=u'权限列表'
        self.fields['id_perm'].required=False

    #permission = forms.MultipleChoiceField(label=u'权 限',required=False,choices=[(x.id,x.name) for x in PermissionList.objects.all()],
    #    widget=forms.CheckboxSelectMultiple())
