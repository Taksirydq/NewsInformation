from . import index_blu
from flask import current_app, jsonify
from info.models import User,News
from flask import render_template
from flask import session
from info.utils.response_code import RET
from info import constants


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
    # ---------------------获取新闻点击排行榜---------------------------------
    try:
        news_rank_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻排行数据异常")
    """
        查询到的是对象列表
       # news_rank_list 对象列表===》 [news1, news2, ...新闻对象 ]
       # news_rank_dict_list 字典列表===> [{新闻字典}, {}, {}]
    """
    # 字典列表初始化
    news_rank_dict_list = []
    # 将新闻对象列表转换成字典列表
    for news_obj in news_rank_list if news_rank_list else []:
        # 将新闻对象转成字典
        news_dict = news_obj.to_dict()
        # 构建字典列表
        news_rank_dict_list.append(news_dict)

    # 组织响应数据字典
    # 如果user存在,我就使用user转换成字典给到其user_info,如果user不存在，就用None替换user.to_dict()
    data = {
        "user_info": user.to_dict() if user else None,
        "news_rank_list":news_rank_dict_list
    }
    return render_template("news/index.html", data=data)


# send_static_file是系统访问静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    """返回网页的图标"""
    return current_app.send_static_file("news/favicon.ico")
