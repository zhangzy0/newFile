# _*_ coding: utf-8 _*_
from django import template
import datetime
import time
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def timedown(value,arg):

    try:
        create_secs = time.mktime(value.timetuple())
        if '内蒙' in str(arg):
            timerepair = create_secs + 129600
        else:
            timerepair = create_secs+86400
        reduce = timerepair - time.time()
        if int(reduce/3600) > 4 :
            result='<span style="color: #11A9CC;">剩余{time}小时</span>'.format(time=int(reduce/3600))
            return mark_safe(result)
        elif 0< int(reduce/3600) <=4:
            result = '<span style="color: #FF9200;">剩余{time}小时</span>'.format(
                time=int(reduce / 3600))
            return mark_safe(result)
        else :
            result = '<span style="color: #EB4C2A;">超过{time}小时</span>'.format(
                time=-int(reduce / 3600))
            return mark_safe(result)
    except Exception,e:
        return ""

