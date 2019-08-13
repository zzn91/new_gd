from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db
from models import *
import models

manager = Manager(app)
migrate = Migrate(app, db)


manager.add_command('db', MigrateCommand)


def make_shell_context():

    return dict(app=app, db=db, model=models)

@manager.command
def create_table():
    # 初始化表结构
    from app import db
    db.create_all()


manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
