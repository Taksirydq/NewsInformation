from info.models import Category, News, User
from info.utils.pic_storage import pic_storage
from info import db, constants
from info.utils.response_code import RET
from . import profile_bp
from flask import render_template, g, request, jsonify, session, current_app
from info.utils.common import user_decorative_device


# 127.0.0.1:5000/user/pic_info
@profile_bp.route('/pic_info', methods=['GET', 'POST'])
@user_decorative_device
def pic_info():
    """更换用户头像后端接口"""
    # 获取用户对象
    user = g.user
    # GET:返回修改用户头像页面
    if request.method == 'GET':
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template('profile/user_pic_info.html', data=data)

    # POST:修改用户头像
    """
    1.获取参数
        1.1 avatar: 用户头像数据， user:用户对象
    2.校验参数
        2.1 非空判断
    3.逻辑处理
        3.1 借助封装好的工具，将二进制图片数据上传到七牛云
        3.2 图片的url保存到用户对象中
        3.3 将完整的图片url返回给前端
    4.返回值
    """
    # 1.获取到上传的文件 avatar: 用户头像数据， user:用户对象
    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="读取文件错误 ")

    # 2.借助封装好的工具，将二进制图片数据上传到七牛云
    try:
        url = pic_storage(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 3.将头像信息更新到当前用户的模型中
    # 图片的url保存到用户对象中
    user.avatar_url = url
    # 将数据保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 数据库回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户数据异常")
    # 组织响应数据字典
    data = {
        "avatar_url": constants.QINIU_DOMIN_PREFIX + url
    }
    # 返回值 将完整的图片url返回给前端
    return jsonify(errno=RET.OK, errmsg="OK", data=data)


# 127.0.0.1:5000/user/pass_info
@profile_bp.route('/pass_info', methods=['GET', 'POST'])
@user_decorative_device
def pass_info():
    """用户密码修改后端接口"""
    #  GET:返回修改用户头像页面
    if request.method == 'GET':
        return render_template('profile/user_pass_info.html')

    """
    1.获取参数
        1.1 old_password:旧密码(原密码), new_password: 新密码 user:用户对象
    2.校验参数
        2.1 非空判断
    3.逻辑处理
        3.1 对就密码进行校验
        3.2 将新密码赋值到user对象password属性上
        3.3 保存回数据库
    4.返回值
    """
    # 1.1 old_password:旧密码(原密码), new_password: 新密码
    params_dict = request.json
    old_password = params_dict.get("old_password")
    new_password = params_dict.get("new_password")
    # 获取到用户登录信息
    user = g.user
    # 2.1 非空判断
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 2.2 用户是否登录判断
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 3.1 对就密码进行校验
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    # 3.2 将新密码赋值到user对象password属性上
    user.password = new_password
    # 3.3 保存回数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 数据库回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="保存成功")


# 127.0.0.1:5000/user/base_info
@profile_bp.route('/base_info', methods=['GET', 'POST'])
@user_decorative_device
def user_base_info():
    """展示用户基本资料页面"""
    # 获取用户对象
    user = g.user
    # TODO:GET:请求查询用户基本资料展示
    if request.method == 'GET':
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("profile/user_base_info.html", data=data)

    # TODO:POST: 请求修改用户基本资料
    """
    1.获取参数
        1.1 signature:个性签名，nick_name:昵称，gender:性别，user:当前登录用户
    2.校验参数
        2.1 非空判断
        2.2 gender in ['MAN','WOMAN']
    3.逻辑处理
        3.1 将获取到的属性保存到当前登录的用户中
        3.2 更新session中的nick_name数据
        3.3 将用户对象保存回数据库
    4.返回值
    """
    # 1.1 signature:个性签名，nick_name:昵称，gender:性别，user:当前登录用户
    params_dict = request.json
    signature = params_dict.get("signature")
    nick_name = params_dict.get("nick_name")
    gender = params_dict.get("gender")

    # 2.1 非空判断
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 2.2 用户是否登录判断
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 2.3gender in ['MAN','WOMAN']
    if gender not in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.PARAMERR, errmsg="action参数错误")

    # 3.1 将获取到的属性保存到当前登录的用户中
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender
    # 3.2 更新session中的nick_name数据
    session["nick_name"] = nick_name
    # 3.3 将用户对象保存回数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存用户对象异常")

    # 返回值
    return jsonify(errno=RET.OK, errmsg="修改用户基本资料成功")


# 127.0.0.1:5000/user/collection?p=页码
@profile_bp.route('/collection')
@user_decorative_device
def user_collection_news():
    """用户收藏新闻后端实现接口"""
    """
    1.获取参数
        1.1 当前用户对象，page:当前页码(默认值第一页)
    2.校验参数
        2.1 非空判断
        2.2 整型强制类型转换
    3.逻辑处理
        3.1 分页查询
        3.2 对象列表转换成字典列表
    4.返回值
    """
    # 获取用户对象
    user = g.user
    p = request.args.get("p", 1)

    # 2.1 参数类型判断
    try:
        # 数据类型转换
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数内容错误")
    # 当前用户存在的时候采取查询
    """
    lazy="dynamic"设置后：
    如果没有真实用到user.collection_news，他就是一个查询对象
    如果真实用到user.collection_news，他就是一个列表
    """
    news_collections = []
    current_page = 1
    total_page = 1
    if user:
        try:
            paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
            # 当前页码所有数据
            news_collections = paginate.items
            # 当前页码
            current_page = paginate.page
            # 总页数
            total_page = paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询收藏新闻分页数据异常")

    # 对象列表转字典列表
    news_dict_collections = []
    for news in news_collections if news_collections else []:
        news_dict_collections.append(news.to_basic_dict())

    # 组织响应数据
    data = {
        "collections": news_dict_collections,
        "current_page": current_page,
        "total_page": total_page
    }

    # 4.返回值
    return render_template("profile/user_collection.html", data=data)


@profile_bp.route('/news_release', methods=['GET', 'POST'])
@user_decorative_device
def news_release():
    """新闻发布的后端接口"""
    # 获取用户对象
    user = g.user

    # GET请求：展示新闻发布页面
    if request.method == 'GET':
        # 查询分类数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询分类数据异常")
        # 对象列表转换成字典列表
        category_dict_list = []
        for category in categories if categories else []:
            category_dict_list.append(category.to_dict())

        # 注意：移除最新分类
        category_dict_list.pop(0)

        # 组织响应数据
        data = {
            "categories": category_dict_list
        }
        return render_template("profile/user_news_release.html", data=data)

    # POST请求: 发布新闻
    """
    1.获取参数
        1.1 title: 新闻标题, category_id: 新闻分类id, digest:新闻摘要，index_image:新闻主图片
            content: 新闻内容，user:当前用户，source:新闻来源（默认值：个人发布）
    2.校验参数
        2.1 非空判断
    3.逻辑处理
        3.1 将新闻主图片上传到七牛云
        3.2 创建新闻对象，并将其属性赋值
        3.3 保存回数据库
    4.返回值
    """
    # 1.1 获取参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    source = "个人发布"

    # 2.1 非空判断
    if not all([title, category_id, digest, content, index_image]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # 2.2 用户是否登录判断
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    try:
        pic_data = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="图片数据不能为空")

    # 3.1 将新闻主图片上传到七牛云　
    try:
        pic_name = pic_storage(pic_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 3.2 创建新闻对象，并将其属性赋值
    news = News()
    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + pic_name
    news.source = source
    news.user_id = user.id
    # 设置新闻发布后的状态: 审核中
    news.status = 1
    # 3.3保存回数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存新闻对象异常")
    # 返回值
    return jsonify(errno=RET.OK, errmsg="新闻发布成功")


@profile_bp.route('/news_list')
@user_decorative_device
def news_list():
    """获取当前用户新闻收藏列表数据"""
    """
    1.获取参数
        1.1 user: 当前用户对象，p:当前页码(默认值第一页)
    2.校验参数
        2.1 非空判断
    3.逻辑处理
        3.1 进行分页查询
    4.返回值
    """
    # 获取用户对象
    user = g.user
    p = request.args.get("p", 1)

    # 2.1 参数判断
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数内容错误")

    # 当用户存在的时候采取查询
    """
    对比：
    当前用户收藏的新闻查询： user.collection_news
    当前用户发布的新闻查询： News.query.filter(News.user_id == user.id)
    """
    news_list = []
    current_page = 1
    total_page = 1
    if user:
        try:
            paginate = News.query.filter(News.user_id == user.id).paginate(p, constants.OTHER_NEWS_PAGE_MAX_COUNT,
                                                                           False)
            # 当前页码所有数据
            news_list = paginate.items
            # 当前页码
            current_page = paginate.page
            # 总页数
            total_page = paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询发布新闻分页数据异常")

        # 对象列表转成字典列表
        news_dict_list = []
        for news in news_list if news_list else []:
            news_dict_list.append(news.to_basic_dict())

        # 组织响应数据
        data = {
            "news_list": news_dict_list,
            "current_page": current_page,
            "total_page": total_page
        }
        # 返回值
        return render_template("profile/user_news_list.html", data=data)


# @profile_bp.route('/followed_user', methods=['POST'])
# @user_decorative_device
# def followed_user():
#     """关注与取消关注用户后端接口"""
#     # 获取用户对象
#     user = g.user
#     # 判断用户是否存在
#     if not user:
#         return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
#
#     # 获取参数 user_id:被关注的用户id action:指定两个值：'follow', 'unfollow'
#     user_id = request.json.get("user_id")
#     action = request.json.get("action")
#
#     # 参数校验
#     if not all([user_id, action]):
#         return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
#     # action["follow", "unfollow"]
#     if action not in ("follow", "unfollow"):
#         return jsonify(errno=RET.PARAMERR, errmsg="参数内容错误")
#
#     # 根据user_id去查询关注的用户信息
#     try:
#         target_user = User.query.get(user_id)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR, errmsg="查询数据异常")
#     if not target_user:
#         return jsonify(errno=RET.NODATA, errmsg="未查询到用户数据")
#
#     # 根据不同的操作做不同的逻辑
#     if action == 'follow':
#         if target_user.followers.filter(User.id == user.id).count() > 0:
#             return jsonify(errno=RET.DATAERR, errmsg="当前用户已关注")
#         target_user.followers.append(user)
#     else:
#         if target_user.followers.filter(User.id == user.id).count() > 0:
#             target_user.followers.remove(user)
#
#     # 保存回数据库
#     try:
#         db.session.commit()
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR, errmsg="保存数据异常")
#     # 返回值
#     return jsonify(errno=RET.OK, errmsg="OK")


# 127.0.0.1:5000/user/info
@profile_bp.route('/info')
@user_decorative_device
def user_info():
    """展示用户个人中心页面"""
    # 获取用户对象
    user = g.user
    data = {
        "user_info": user.to_dict() if user else None
    }
    return render_template('profile/user.html', data=data)
