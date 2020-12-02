from django.conf.urls import url
from django.views.static import serve
from BBS import settings

from account import views

urlpatterns = [
    url(r'^backend/$', views.backend, name='backend'),  # 后台管理
    url(r'^up_or_down/$', views.up_or_down, name='up_or_down'),  # 点赞点踩
    url(r'^comment/$', views.comment, name='comment'),  # 点赞点踩
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^get_code/$', views.get_code, name='get_code'),  # 验证码
    url(r'^home/$', views.home, name='home'),  # 首页
    url(r'^set_password/$', views.set_password, name='set_password'),  # 修改密码
    url(r'^logout/$', views.logout, name='logout'),  # 修改密码
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),  # 暴露静态资源
    url(r'^(?P<username>\w+)/$', views.site, name='site'),  # 个人站点搭建
    # 侧边栏筛选功能
    # url(r'^(?P<username>\w+)/category/(\d+)/$', views.site),
    # url(r'^(?P<username>\w+)/tag/(\d+)/$', views.site),
    # url(r'^(?P<username>\w+)/archive/(\w+)/$', views.site),
    # 合并侧边栏筛选url
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/$', views.site),
    # 文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/$', views.article_detail),

]
