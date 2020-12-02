# !/usr/bin/env Python
# -*- coding:utf-8 -*-
#

from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from account import models

register = template.Library()


# 自定义inclusion_tag
@register.inclusion_tag('blogs/left_menu.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 构造侧边栏需要的数据
    # 统计当前用户所有分类及分类下的文章数
    # values 结果列表套字典  values_list 列表套元组
    # category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values('name', 'count_num')
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name', 'count_num', 'pk')
    # 查询当前用户所有标签及标签下文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name',
                                                                                                         'count_num',
                                                                                                         'pk')
    # 按照年月统计所有文章
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_num=Count('pk')).values_list('month', 'count_num')
    return locals()
