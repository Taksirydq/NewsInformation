from info import constants, db
from info.models import News
from info.utils.common import user_decorative_device
from info.utils.response_code import RET
from . import news_bp
from flask import render_template, current_app, jsonify, g, request


# 127.0.0.1:5000/news/news_collect
@news_bp.route('/news_collect', methods=['POST'])
@user_decorative_device
def news_collect():
    """点击收藏/取消收藏的后端接口实现"""
    """
    1.获取参数
        1.1 news_id：当前新闻id，action:收藏或取消收藏的行为('collect', 'cancel_collect')
    2.校验参数
        2.1 非空判断
        2.2 action必须在['collect', 'cancel_collect']列表内
    3.逻辑处理
        3.1 根据新闻id查询对象
        3.2 收藏: 将当前新闻添加到user.collection_news列中
        3.3 取消收藏: 将当前新闻从user.collection_news列中移除
    4.返回值
    """
    # 1.1 news_id：当前新闻id，action:收藏或取消收藏的行为('collect', 'cancel_collect')
    param_dict = request.json
    news_id = param_dict.get('news_id')
    action = param_dict.get('action')
    # 获取当前登录的用户对象
    user = g.user
    # 2.1 非空判断
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 判断用户是否有登录
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 2.2action必须在['collect', 'cancel_collect']列表内
    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg="参数的内容错误")

    # 3.1根据新闻id查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻数据异常")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 3.2 收藏: 将当前新闻添加到user.collection_news列中
    if action == "collect":
        # 收藏
        user.collection_news.append(news)
    # 3.3 取消收藏: 将当前新闻从user.collection_news列中移除
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)

    # 将用户收藏列表的修改操作保存回数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存新闻列表数据异常")

    # 返回值
    return jsonify(errno=RET.OK, errmsg="OK")


# 127.0.0.1:5000/news/1
@news_bp.route('/<int:news_id>')
@user_decorative_device
def news_detail(news_id):
    """展示新闻详情首页"""
    # -----------------获取用户登录信息-------------------------
    # 从装饰器的g对象中获取到当前登录的用户
    user = g.user
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
    news_dict_list = []
    # 将新闻对象列表转换成字典列表
    for news_obj in news_rank_list if news_rank_list else []:
        # 将新闻对象转成字典
        news_dict = news_obj.to_dict()
        # 构建字典列表
        news_dict_list.append(news_dict)

    # ------------------获取新闻详情数据--------------------------
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻详情数据异常")
    # 将新闻详情对象转换成字典
    news_dict = news.to_dict() if news else None

    # 用户浏览量累加
    news.clicks += 1

    # ---------------------查询当前用户是否收藏当前新闻-------------
    # is_collected = True 表示当前用户收藏过该新闻(false反之)
    is_collected = False
    # 当前用户已经登录
    if user:
        if news in user.collection_news:
            # 当前新闻在用户的新闻收藏列表内，表示已经收藏
            is_collected = True

    # 组织响应数据字典
    data = {
        "user_info": user.to_dict() if user else None,
        "news_rank_list": news_dict_list,
        "news": news_dict,
        "is_collected": is_collected
    }

    return render_template("news/detail.html", data=data)
