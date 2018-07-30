#!/usr/bin/env python 
#*- coding: utf-8 -*-
"""
#author :liuzhen
#date   :20160512
#function: 
"""

from apps.usermanage.models import User
from rest_framework import serializers

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, max_length=1024)
    password = serializers.CharField(required=False, max_length=1024)
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
