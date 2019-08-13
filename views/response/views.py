from flask import Blueprint, request, jsonify
from models import Response, Task
from app import db
import json

response_bp = Blueprint('response_bp', __name__)

__author__ = "Zhaozn"


@response_bp.route('/save_task_url', methods=["POST"])
def save_response():
    '''
    获取任务ID及保存的图片路径地址
    :return:
    '''
    if request.json is None:
        return jsonify(code=10001, msg='未传递参数')

    task_list = request.json.get('task_list', None)

    if task_list is None:
        return jsonify(code=10001, msg='未传递参数')

    if not isinstance(task_list, list):
        return jsonify(code=10001, msg='未传递参数')

    task_list = task_list

    task_list = [Task(object_url=task.get('object_url'),
                              task_id=task.get('task_id')) for task in task_list]


    db.session.add_all(task_list)
    db.session.commit()

    return jsonify(code=200, msg='SUCCESS')

@response_bp.route('/get_task_url/<task_id>', methods=["GET"])
def get_task_url(task_id):

    if task_id is None:
        return jsonify(code=10001, msg='未传递参数')

    task = Task.query.filter_by(task_id=task_id).first()

    if task is None:
        return jsonify(code=10002, msg='参数不正确')

    data = {
        'task_id': task.task_id,
        'object_url': task.object_url
    }

    return jsonify(code=200, data=data)


@response_bp.route('/post_response', methods=["POST"])
def post_response():
    if request.json is None:
        return jsonify(code=10001, msg='未传递参数')

    user_resp = request.json.get('user_resp', None)
    task_id = request.json.get('task_id', None)
    id = request.json.get('id', None)

    if user_resp and task_id and id:
        response = db.session.query(Response).filter(Response.response_id == id).count()
        if response:
            return jsonify(code=10001, msg='当前回答已存在')

        response = Response()
        response.response_id = id
        response.user_resp = user_resp
        response.task_id = task_id

        db.session.add(response)
        db.session.commit()

        return jsonify(code=200, msg='SUCCESS')

    return jsonify(code=10001, msg='未传递参数')



@response_bp.route('/get_response/<response_id>', methods=["GET"])
def get_response(response_id):
    if response_id is None:
        return jsonify(code=10001, msg='未传递参数')

    response = Response.query.filter_by(response_id=response_id).first()

    if response is None:
        return jsonify(code=10002, msg='此回答不存在')

    data = {'user_resp': json.loads(response.user_resp)}

    return jsonify(code=200, data=data)
