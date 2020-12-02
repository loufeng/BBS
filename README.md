# BBS

Django==1.11.29

Python==3.6.8

BBS表设计

```
用户表
	继承AbstractUser
	扩展
		phone	电话号码
		avatar	用户头像
		create_time	创建时间
		
		外键字段
		一对一个人站点表
		
个人站点表
	site_name 站点名称
  site_title	站点标题
  site_theme	站点样式
  
文章标签表
	name	标签名
	
	外键字段
		一对多个人站点
	
文章分类表
	name	分类名
	
	外键字段
		一对多个人站点
	
文章表
	title	文章标题
  desc	文章简介
  content	文章内容
  create_time	分布时间
  up_num	点赞数
  down_num	点踩数
  comment_num	评论数
	数据库设计优化点
  	(点赞数、点踩数、评论数可以从其他表里跨表查询得出，但是频繁跨表影响效率）
  	
    外键字段
    	一对多个人站点
    	多对多文章标签
    	一对多文章分类
  
点赞点踩表
	user	ForeginKey(to="User")
	article	ForeginKey(to="Article")
	is_up  BooleanField()
	
文章评论表
	user	ForeginKey(to="User")
	article	ForeginKey(to="Article")
	content	CharField()
	comment_time	DateField()
	# 自关联
	parent ForeginKey(to="Comment", null=True)
	# ORM提供自关联写法
	parent ForeginKey(to="self", null=True)
```

