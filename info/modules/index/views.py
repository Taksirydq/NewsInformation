from info.utils.common import user_decorative_device
from . import index_blu
from flask import current_app, jsonify, g
from info.models import User, News, Category
from flask import render_template
from flask import session,request
from info.utils.response_code import RET
from info import constants


# 　2.使用蓝图
@index_blu.route('/')
@user_decorative_device
def index():
    """新闻首页"""
    # ----------------获取用户登录信息----------------------------------

    # 从装饰器的g对象中获取到登录的用户
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

    # ---------------------------新闻分类展示----------------------------------
    try:
        # 获取新闻分类数据
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻分类数据异常")
    # 定义列表保存分类数据
    categories_dicts = []

    for category in categories:
        # 拼接内容
        categories_dicts.append(category.to_dict())

    # 组织响应数据字典
    # 如果user存在,我就使用user转换成字典给到其user_info,如果user不存在，就用None替换user.to_dict()
    data = {
        "user_info": user.to_dict() if user else None,
        "news_rank_list": news_dict_list,
        "categories": categories_dicts
    }
    return render_template("news/index.html", data=data)


# --------------------------新闻列表后端实现-------------------------------------
@index_blu.route('/news_list')
def get_news_list():
    """获取新闻列表数据后端接口(get)"""
    """
    获取指定分类的新闻列表
        1.获取参数
            1.1 cid:分类id, page:当前页码(默认值:第一页)，per_page:每一页多少条数据(默认值:10条) (数据类型json)          
        2.校验参数
            2.1 非空判断
            2.2 整型强制类型转换
        3.逻辑处理
            3.1 分页查询
            3.2 对象列表转换成字典列表
        4.返回值
    """
    # 1.1 cid:分类id, page:当前页码(默认值:第一页)，per_page:每一页多少条数据(默认值:10条) (数据类型json)
    param_dict = request.args
    cid = param_dict.get('cid')
    page = param_dict.get('page', '1')
    per_page = param_dict.get('per_page', "10")
    # 2.1 非空判断
    if not cid:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 2.2 整型强制类型转换
    try:
        # 进行数据类型转换
        page = int(page)
        per_page = int(per_page)
        cid = int(cid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数内容格式错误")
    # 条件列表
    filters = [News.status == 0]
    # 如果分类id不为1，那么添加分类id的过滤
    if cid != 1:
        # ==在sqlalchemy底层有重写__eq__方法，改变了该返回值，返回是一个查询条件
        filters.append(News.category_id == cid)
    # 3.1查询数据并分页 *filters拆包
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        # 获取查询出来所有的数据
        news_list = paginate.items
        # 获取到总页数
        total_page = paginate.pages
        # 当前页码
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻列表数据异常")
    # 3.2对象列表转换成字典列表
    news_dict_list = []
    for news in news_list if news_list else []:
        news_dict_list.append(news.to_dict())
    # 组织响应数据字典
    data = {
        "news_list": news_dict_list,
        "current_page": current_page,
        "total_page": total_page

    }
    # 返回值
    return jsonify(errno=RET.OK, errmsg="查询新闻列表数据成功", data=data)


# send_static_file是系统访问静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    """返回网页的图标"""
    return current_app.send_static_file("news/favicon.ico")
