#!/usr/bin/env python
#-*- coding: utf-8 -*-

#import ast
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.
class AppList(models.Model):
    id_app = models.AutoField(primary_key=True)
    app_en = models.CharField(max_length=20)
    app_cn = models.CharField(max_length=80)

    def __unicode__(self):
        return self.app_cn

class PermissionList(models.Model):
    id_perm = models.AutoField(primary_key=True)
    per_en = models.CharField(max_length=64)
    per_cn = models.CharField(max_length=64)
    per_url = models.CharField(max_length=255)
    per_pid = models.IntegerField()
    per_level = models.IntegerField()
    per_icon = models.CharField(max_length=63)
    id_app = models.ForeignKey(AppList,null=True,blank=True)
    per_guid = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s(%s)' %(self.per_cn,self.per_url)

                                              
class RoleList(models.Model):
    id_role = models.AutoField(primary_key=True)
    role_en = models.CharField(max_length=64)
    role_cn = models.CharField(max_length=64)
    id_perm = models.ManyToManyField(PermissionList,related_name='role_permission',null=True,blank=True)
    #permission = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return self.role_cn


class SpecialDays(models.Model):
    sp_date = models.DateField(primary_key=True)
    def __unicode__(self):
        return self.sp_date

class UserManager(BaseUserManager):
    def create_user(self,email,username,realname,password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            realname = realname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,realname,password):
        user = self.create_user(email,
            username = username,
            realname = realname,
            password = password,
        )

        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True, db_index=True)
    email = models.EmailField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    realname = models.CharField(max_length=64, null=True)
    #sex = models.CharField(max_length=2, null=True)
    role = models.ForeignKey(RoleList,null=True,blank=True)
    u_create_id_user = models.IntegerField(null=True)
    u_create_time = models.DateTimeField(auto_now_add=True)
    u_mphone = models.CharField(max_length=15, null=True)
    u_modify_id_user = models.IntegerField(null=True)
    u_modify_time = models.DateTimeField(auto_now=True)
    # add 
    #is_staff = models.BooleanField(default=False)
    

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','realname']

    def has_perm(self,perm,obj=None):
        if self.is_active and self.is_superuser:
            return True

    def __unicode__(self):
        return self.realname
