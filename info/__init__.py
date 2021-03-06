from redis import StrictRedis
import logging
from flask import Flask, g, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session
from config import config_dict
from logging.handlers import RotatingFileHandler

# 暂时没有app对象，就不会去初始化，只是声明一下
from info.utils.common import do_index_class, user_decorative_device

db = SQLAlchemy()
# redis数据库对象的声明（全局变量）
redis_store = None


def setup_log(config_name):
    """配置日志"""

    # 根据传入配置字符串获取不同配置
    configClass = config_dict[config_name]

    # 设置日志的记录等级
    logging.basicConfig(level=configClass.LOG_LEVEL)  # 调试debug级

    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """通过传入不同的配置名字,　初始化其对应配置的应用实例"""
    # 0.记录日志
    setup_log(config_name)
    # 1.创建app对象
    app = Flask(__name__)

    # development --> DevelopmentConfig 开发模式的配置类
    # production --> ProductionConfig 线上模式的配置类
    configClass = config_dict[config_name]
    # 将配置类注册到app上 根据不同的配置类，赋予不同模式的app
    app.config.from_object(configClass)

    # 创建数据库对象
    db.init_app(app)
    # 创建redis数据库对象(懒加载思想)
    global redis_store
    redis_store = StrictRedis(host=configClass.REDIS_HOST,
                              port=configClass.REDIS_PORT,
                              db=configClass.REDIS_NUM,
                              decode_responses=True
                              )

    """
      #4.开启csrf保护机制
      1.自动获取cookie中的csrf_token,
      2.自动获取ajax请求头中的csrf_token
      3.自己校验这两个值
      """
    # 开启csrf保护
    CSRFProtect(app)

    # 使用钩子函数将csrf_token带回给浏览器
    @app.after_request
    def set_csrftoken(response):
        """借助response.setcookie方法将csrf_token存储到浏览器"""
        # 1.生成csrf_token随机值
        csrf_token = generate_csrf()
        # 2.设置cookie
        response.set_cookie("csrf_token", csrf_token)
        # 返回响应对象
        return response

    # 捕获404异常，页面统一处理
    @app.errorhandler(404)
    @user_decorative_device
    def error_handler(err):
        # 1.获取用户对象
        user = g.user
        # 2.对象转成字典
        data = {
            "user_info": user.to_dict() if user else None
        }
        # 3.渲染模板
        return render_template("news/404.html", data=data)

    # 添加自定义的过滤器
    app.add_template_filter(do_index_class, "do_index_class")

    # 设置session保存位置,将session的存储方法进行调整（flask后端内存---> redis数据库）
    Session(app)

    # 注册首页蓝图
    # 真正用到蓝图对象的时候才导入，延迟导入（只有函数被调用才会来导入），解决循环导入问题
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    # 注册登录模块蓝图
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    # 注册新闻模块蓝图
    from info.modules.news import news_bp
    app.register_blueprint(news_bp)

    # 注册个人中心蓝图
    from info.modules.profile import profile_bp
    app.register_blueprint(profile_bp)

    # 注册用户管理模块蓝图
    from info.modules.admin import admin_bp
    app.register_blueprint(admin_bp)
    # 返回不同模式下的app对象
    return app
