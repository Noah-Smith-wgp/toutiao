from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from project import app, db


# 使用Manager接管app
manager = Manager(app)

# 让Migrate迁移类绑定app和db
Migrate(app=app, db=db)

# 将迁移指令添加到Manager中
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
