from django.conf.urls import patterns, include, url

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('apps.usermanage.views',
    url(r'^$', 'comm.Home'),
    url(r'^login/$', 'user.LoginUser'),
    url(r'^logout/$', 'user.LogoutUser'),

    url(r'^user/add/$', 'user.AddUser'),
    url(r'^user/list/$', 'user.ListUser'),
    url(r'^user/edit/(?P<ID>\d+)/$', 'user.EditUser'),
    url(r'^user/delete/(?P<ID>\d+)/$', 'user.DeleteUser'),

    url(r'^user/changepwd/$', 'user.ChangePassword'),
    url(r'^user/resetpwd/(?P<ID>\d+)/$', 'user.ResetPassword'),

    url(r'^role/add/$', 'role.AddRole'),
    url(r'^role/list/$', 'role.ListRole'),
    url(r'^role/edit/(?P<ID>\d+)/$', 'role.EditRole'),
    url(r'^role/delete/(?P<ID>\d+)/$', 'role.DeleteRole'),

    url(r'^permission/deny/$', 'permission.NoPermission'),

    url(r'^permission/add/$', 'permission.AddPermission'),
    url(r'^permission/list/$', 'permission.ListPermission'),
    url(r'^permission/edit/(?P<ID>\d+)/$', 'permission.EditPermission'),
    url(r'^permission/delete/(?P<ID>\d+)/$', 'permission.DeletePermission'),
)
