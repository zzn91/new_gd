# -*- coding: utf-8 -*-
import json

import requests
from flask import request, jsonify

from api.tagging.tagging_util import req_util
from models import Response
from app import db

def tagging_get_func(url, headers):
    resp = requests.post(url=url,
                                 cookies=request.cookies,
                                 json=request.json,
                                 headers=headers)


    # if resp.status_code == 200:
    #     # try:
    #     resp_content = json.loads(resp.content)
    #     content = resp_content.get('content')
    #     if not content:
    #         return jsonify(code=200, content=[])
    #
    #     for response in content:
    #         print(response)
    #         resp = db.session.query(Response).filter(Response.response_id == response.get('id')).first()
    #         if resp:
    #             response['object_url'] = resp.object_url
    #
    #     return jsonify(code=200, content=content)
    #     # except Exception as e:
    #     #     return jsonify(code=444, msg=e)
    #
    # return jsonify(code=200, content=[])

    filter_info = {'filter_key': 'id', 'filter_value': ['object_url']}
    return req_util(resp, Response, filter_fields=['content'], filter_info=filter_info)

