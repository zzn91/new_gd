import requests
from flask import Blueprint, request, jsonify

from api.tagging.tagging_util import req_util
from models import Response, Task
from app import db
import json

from util.request_obj import get_url

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
                         headers={'Referer': 'http://127.0.0.1:8008/66635'})

    filter_info = {'filter_key': 'id', 'filter_value': ['object_url']}
    return req_util(resp, Response, filter_fields=['content'], filter_info=filter_info)


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
                         headers={'Referer': 'http://127.0.0.1:8008/66635'})

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
        response = Response()
        response.response_id = id
        response.user_resp = json.dumps(user_resp)
        db.session.add(response)

    db.session.commit()

    return jsonify(resp_data)


