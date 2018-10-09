from flask import Blueprint

# 创建蓝图， 并设置蓝图前缀
news_bp = Blueprint("news", __name__, url_prefix='/news')

# 导入views文件中的视图函数
from .views import *