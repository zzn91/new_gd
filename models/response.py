from .Base import BaseModel
from app import db




class Task(BaseModel):
    __tablename__ = 'task'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    task_id = db.Column(db.Integer, index=True, comment='任务ID')
    object_url = db.Column(db.Text, default='', comment='图片路径')


class Response(BaseModel):

    __tablename__ = 'response'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    response_id = db.Column(db.String(64), index=True, comment='回答ID')
    cache_id = db.Column(db.String(64), index=True, comment='缓存ID')
    user_resp = db.Column(db.Text, default='', comment='用户回答结果')
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), index=True, comment='任务ID')
    object_url = db.Column(db.Text, default='', comment='图片路径')
