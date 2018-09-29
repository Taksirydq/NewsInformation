from flask import Blueprint

# 创建蓝图， 并设置蓝图前缀
passport_blu = Blueprint("passport", __name__, url_prefix='/passport')

# 导入views文件中的视图函数
from . import views