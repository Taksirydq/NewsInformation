from info import db
from info.models import User
from . import admin_bp
from flask import render_template, request, session, redirect, url_for, current_app


# admin/index
@admin_bp.route('/index')
def admin_index():
    """后台管理首页"""
    return render_template("admin/index.html")


# /admin/login
@admin_bp.route('/login', methods=['POST', 'GET'])
def admin_login():
    """后台管理登录接口"""
    # GET请求: 展示登录页面
    if request.method == 'GET':
        # 判断管理员用户是否登录，如果管理员有登录直接进入管理首页(提高用户体验)
        user_id = session.get("username")
        is_admin = session.get("is_admin", False)
        if user_id and is_admin:
            # 当前用户登录& is_admin=True表示管理员
            return redirect(url_for("admin.admin_index"))
        else:
            # 不是管理员用户
            return render_template("admin/login.html")

    # POST请求：管理员登录业务逻辑处理
    """
    1.获取参数
        1.1 username: 账号，password: 密码
    2.校验参数
        2.1 非空判断
    3.逻辑处理
        3.1 根据username查询用户
        3.2 name.check_password进行密码校验
        3.3 管理员用户数据保存到session
    4.返回值
        4.1 跳转到管理首页
    """
    # 1.1 username: 账号，password: 密码
    username = request.form.get("username")
    password = request.form.get("password")
    # 2.1 非空判断
    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数不足")
    # 3.1 根据username查询用户
    try:
        admin_user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="查询管理员用户对象异常")
    if not admin_user:
        return render_template("admin/login.html", errmsg="管理员用户不存在")

    # 3.1 user.check_password进行密码校验
    if not admin_user.check_password(password):
        return render_template("admin/login.html", errmsg="密码填写错误")

    # 保存回数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return render_template("admin/login.html", errmsg="保存用户对象异常")

    # 3.2 管理员用户数据保存到session
    session["nick_name"] = username
    session["user_id"] = admin_user.id
    session["mobile"] = username
    session["is_admin"] = True

    # 4.重定向到管理首页
    return redirect(url_for("admin.admin_index"))
