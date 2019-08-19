import requests
from flask import Blueprint, request, jsonify

from api.tagging.tagging_util import req_util
from models import Response, Task
from app import db
import json

from util.request_obj import get_url, get_headers

response_bp = Blueprint('response_bp', __name__)

__author__ = "Zhaozn"



@response_bp.route('/tagging/get', methods=["POST"])
def tagging_get():
    '''
    获取任务
    :return:
    '''
    resp = requests.post(url=get_url(),
                         cookies=request.cookies,
                         json=request.json,
                         headers=get_headers())

    filter_info = {'filter_key': 'task_id', 'filter_value': ['object_url'], 'field': 'filter_obj.task_id == %s'}
    return req_util(resp, Task, filter_fields=['content'], filter_info=filter_info)


@response_bp.route('/tagging/submit', methods=["POST"])
def tagging_submit():
    '''
    提交任务
    :return:
    '''
    if not request.json:
        return jsonify(code=10001, msg='未传递参数')

    id = request.json.get('id', None)
    user_resp = request.json.get('user_resp', None)
    not_tagging = request.json.get('not_tagging', None)
    edit_submit = request.json.get('edit_submit', None)

    if id is None or (user_resp is None and not_tagging is None):
        return jsonify(code=10001, msg='未传递参数')


    data_dict = request.json

    if data_dict.get('user_resp', None):
        data_dict['user_resp'] = {k: [1 for i in v] for k, v in user_resp.items()}


    resp = requests.post(url=get_url(), cookies=request.cookies, json=request.json,
                         headers=get_headers())

    if resp.status_code != 200:
        return jsonify(resp.content)

    resp_data = json.loads(resp.content)

    if resp_data.get('code') != 200:
        return jsonify(resp_data)

    if edit_submit:
        response = db.session.query(Response).filter(Response.response_id == id).first()
        if response is None:
            return jsonify(code=10001, msg='此回答不存在')

        response.user_resp = json.dumps(user_resp)
    else:
        resp_content = json.loads(resp.content)
        if resp_content.get('code') != 200:
            return jsonify(resp_data)

        task = Task.query.filter_by(task_id=resp_content.get('task_id')).first()
        if task is None:
            return jsonify(code=10001, msg='此任务不存在')
        response = Response()
        response.response_id = resp_content.get('response')
        response.cache_id = id
        response.object_url = task.object_url
        response.task_id = resp_content.get('task_id')
        response.user_resp = json.dumps(user_resp)
        db.session.add(response)

    db.session.commit()

    return jsonify(resp_data)


@response_bp.route('/tagging/check', methods=["POST"])
@response_bp.route('/tagging/check/min', methods=["POST"])
@response_bp.route('/tagging/platform/check/min', methods=["POST"])
@response_bp.route('/tagging/platform/check', methods=["POST"])
def tagging_check():
    '''
    检查任务
    :return:
    '''
    resp = requests.post(url=get_url(),
                         cookies=request.cookies,
                         json=request.json,
                         headers=get_headers())
    filter_info = {'filter_key': 'id',
                   'filter_value': ['object_url', 'user_resp'],
                   'field': 'filter_obj.response_id == %s'}

    return req_util(resp, Response, filter_fields=['content'], filter_info=filter_info)



@response_bp.route('/tagging/sampling_check', methods=["POST"])
@response_bp.route('/tagging/sampling_check/inner_list', methods=["POST"])
@response_bp.route('/tagging/platform/sampling/min', methods=["POST"])
@response_bp.route('/tagging/platform/sampling_check', methods=["POST"])
def tagging_sampling_check():
    '''
    抽检任务
    :return:
    '''
    resp = requests.post(url=get_url(),
                         cookies=request.cookies,
                         json=request.json,
                         headers=get_headers())

    filter_info = {'filter_key': 'cache_id', 'filter_value': ['object_url', 'user_resp']}
    return req_util(resp, Response, filter_fields=['content'], filter_info=filter_info)


