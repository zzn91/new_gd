from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config.config import config
app = Flask(__name__)
db = SQLAlchemy()


# 初始化配置文件
config = config.get('default')
app.config.from_object(config)

# 初始化数据库
db.init_app(app)





