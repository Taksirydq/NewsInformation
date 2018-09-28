from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db


# 创建app,　并传入配置模式: development/production(工厂方法)
app = create_app("development")

# 创建迁移对象
Migrate(app, db)
# 创建管理类
manager = Manager(app)
# 通过管理类添加数据库迁移指令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
