from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views.generic import View

from apps.celeryapi.tasks import _do_kground_work

class Hello(View):

    def get(self, request, *args, **kwargs):
        _do_kground_work.delay('GreenPine')
        return HttpResponse('Hello, World!')
