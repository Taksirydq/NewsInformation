from flask import Blueprint

# 创建蓝图， 并设置蓝图前缀
admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

# 导入views文件中的视图函数
from .views import *