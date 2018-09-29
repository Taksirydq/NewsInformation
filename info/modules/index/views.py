from . import index_blu
from flask import current_app
from info.models import User
from flask import render_template


# 　2.使用蓝图
@index_blu.route('/')
def hello_world():
    return render_template("news/index.html")


# send_static_file是系统访问静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    """返回网页的图标"""
    return current_app.send_static_file("news/favicon.ico")
