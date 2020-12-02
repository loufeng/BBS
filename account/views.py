import json

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, F
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from account import models
from account.froms import MyRegForm


# Create your views here.
def register(request):
    back_dic = {'code': 1000, 'msg': ''}
    form_obj = MyRegForm()

    if request.method == 'POST':
        # 校验数据是否合法
        form_obj = MyRegForm(request.POST)
        # 判断数据是否合法
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data  # 校验通过数据赋值变量

            # 将字典里面的confirm_password 键值对删除
            clean_data.pop('confirm_password')
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data['avatar'] = file_obj
            # 直接操作数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/account/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'blogs/register.html', locals())


def login(request):
    back_dic = {'code': 1000, 'msg': ''}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 先校验验证码是否正确
        if request.session.get('code').upper() == code.upper():
            # 校验用户名和密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                back_dic['url'] = '/account/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名和密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'blogs/login.html', locals())


from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

'''
Image: 生成图片
ImageDraw: 能够在图片上乱涂乱画
ImageFont：控制字体样式
BytesIO：临时存储数据，返回二进制数据
'''


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    img_obj = Image.new('RGB', (200, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/NewYorkItalic.ttf', 30)
    # 随机验证码 五位验证码 数字 大小写字母
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 随机选择一个验证字符串
        tmp = random.choice([random_upper, random_lower, random_int])
        # 将产生的随机字符串写入图片
        '''
        一个个写每个字符串能够控制字体间隙
        '''
        img_draw.text((i * 43, 0), tmp, get_random(), img_font)
        # 拼接字符串
        code += tmp
    # 随机验证码登录视图需要用到，存储到seeeion
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')

    return HttpResponse(io_obj.getvalue())


def home(request):
    # 查询网址所有文章展示，可以使用分页器
    article_queryset = models.Article.objects.all()
    return render(request, 'blogs/home.html', locals())


@login_required
def set_password(request):
    back_dic = {'code': 1000, 'msg': ''}
    if request.is_ajax():
        if request.method == "POST":
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            if is_right:
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg'] = '密码修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
    return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/account/home/')


def site(request, username, **kwargs):
    """
    :param request:
    :param username:
    :param kwargs:  如果有值，做额外操作
    :return:
    """
    # 先校验用户名对应的站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 如果用户不存在返回404页面
    if not user_obj:
        return render(request, 'blogs/404.html')
    blog = user_obj.blog
    # 查询当前个人站点下所有文章
    article_list = models.Article.objects.filter(blog=blog)
    if kwargs:
        # print(kwargs) # {'condition': 'tag', 'param': '1'}
        condition = kwargs['condition']
        param = kwargs['param']
        # 判断根据哪个条件进行筛选
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    # 构造侧边栏需要的数据
    # 统计当前用户所有分类及分类下的文章数
    # values 结果列表套字典  values_list 列表套元组
    # category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values('name', 'count_num')
    # category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
    #     'name', 'count_num', 'pk')
    # # 查询当前用户所有标签及标签下文章数
    # tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name',
    #                                                                                                      'count_num',
    #                                                                                                      'pk')
    # # 按照年月统计所有文章
    # date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
    #     'month').annotate(count_num=Count('pk')).values_list('month', 'count_num')
    return render(request, 'blogs/site.html', locals())


def article_detail(request, username, article_id):
    """
    应该需要校验username和article_id是否存在，这里只完成正确情况
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 先获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    if not article_obj:
        return render(request, 'blogs/404.html')
    # 获取当前文章所有评论列表
    comment_list = models.Comment.objects.filter(article=article_obj)

    return render(request, 'blogs/artilce_detail.html', locals())


def up_or_down(request):
    """
    1. 校验用户是否登录
    2. 判断当前文章是否是当前用户自己写的（自己不能点自己的文章）
    3. 判断当前用户是否已经给当前文章点踩，若已点，不能再点
    4. 操作数据库
    :param request:
    :return:
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        article_id = request.POST.get('article_id')
        is_up = request.POST.get('is_up')
        is_up = json.loads(is_up)  # 转换前端str类型为bool类型
        # 判断用户是否登录
        if request.user.is_authenticated:
            # 判断当前文章是否是当前用户自己写的，根据文章id查询文章对象，根据文章对象查作者，和request.user 进行对比
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                # 校验当前用户是否已经点了
                is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    # 操作数据库，记录数据，要同步操作普通字段
                    # 判断当前用户是点赞还是点踩，从而决定给哪个字段加一
                    if is_up:
                        # 给点赞数加一
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        # 给点踩数加一
                        models.Article.objects.filter(pk=article_id).update(up_num=F('down_num') + 1)
                        back_dic['msg'] = '点踩成功'
                    # 操作点赞点踩表
                    models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '你已经点过了，不能再点了'  # 这里可以坐的更详细，确认是点过赞还是踩
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '不能给自己的文章点'

        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '请先<a href="/account/login/">登录</a>'
    return JsonResponse(back_dic)


def comment(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                print(parent_id)
                # 直接操作评论表，存储数据。两张表
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content, parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '用户未登录'
    return JsonResponse(back_dic)

@login_required
def backend(request):
    return render(request, 'backend/backend.html')