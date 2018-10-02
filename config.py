from redis import StrictRedis
import logging


class Config(object):
    """工程配置信息(父类配置)"""
    DEBUG = True
    # 默认日志等级
    LOG_LEVEL = logging.DEBUG

    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    # 关闭数据库修改跟踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 能替换 db.session.commit()
    # 当数据库会话对象结束的时候自动帮助提交更新数据到数据库
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_NUM = 6

    # 加密字符串
    SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC"
    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT,db=REDIS_NUM)  # 使用 redis 的实例
    SESSION_PERMANENT = False  # 关闭永久存储
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期(24小时)，单位是秒


class DevelopementConfig(Config):
    """开发模式下的配置"""
    DEBUG = True

    # 开发模式的日志级别:DEBUG
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """生产模式下的配置"""
    DEBUG = False

    LOG_LEVEL = logging.WARNING


# 给外界暴露一个使用配置类的接口
# 定义配置字典
config_dict = {
    "development": DevelopementConfig,
    "production": ProductionConfig
}
