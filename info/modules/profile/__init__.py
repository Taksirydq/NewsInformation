from flask import Blueprint

# 创建蓝图， 并设置蓝图前缀
profile_bp = Blueprint("profile", __name__, url_prefix='/user')

# 导入views文件中的视图函数
from .views import *