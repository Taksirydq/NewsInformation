from flask import Blueprint
# 1.创建蓝图对象
index_blu = Blueprint("index", __name__)


# 导入views文件中的视图函数
from . import views