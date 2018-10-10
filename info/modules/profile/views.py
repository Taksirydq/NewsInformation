from info import db
from info.utils.response_code import RET
from . import profile_bp
from flask import render_template, g, request, jsonify, session, current_app
from info.utils.common import user_decorative_device


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
