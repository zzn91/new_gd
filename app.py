from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

from config.config import config
app = Flask(__name__)
db = SQLAlchemy()


# 初始化配置文件
config = config.get('default')
app.config.from_object(config)
xredis = StrictRedis(host='127.0.0.1', port=6379, db=2, charset='utf-8', decode_responses=True)

# 初始化数据库
db.init_app(app)
