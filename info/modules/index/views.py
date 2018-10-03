from . import index_blu
from flask import current_app, jsonify
from info.models import User
from flask import render_template
from flask import session
from info.utils.response_code import RET


# 　2.使用蓝图
@index_blu.route('/')
def index():
    """新闻首页"""
    # ----------------获取用户登录信息----------------------------------
    # 1. 获取当前用户登录的id
    user_id = session.get("user_id")
    user = None  # type:User
    # 2.查询用户对象
    if user_id:
        try:
            # 获取到用户对象
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")
    # 3.将对象转换成字典

    """
    基本格式:
    if user:
        user_info = user.to_dict()
    
    数据格式:
        "data":{
            "user_info":{"id":self.id}
        }
        使用方式：data.user_info.id
    """
    # 组织响应数据字典
    # 如果user存在,我就使用user转换成字典给到其user_info,如果user不存在，就用None替换user.to_dict()
    data = {
        "user_info": user.to_dict() if user else None,
    }
    return render_template("news/index.html", data=data)


# send_static_file是系统访问静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    """返回网页的图标"""
    return current_app.send_static_file("news/favicon.ico")
