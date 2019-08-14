# -*- coding: utf-8 -*-
import json

import requests
from flask import request, jsonify

from api.tagging.tagging_util import req_util
from models import Response


def tagging_get_func(url, headers):
    tagging_resp = requests.post(url=url,
                                 cookies=request.cookies,
                                 json=request.json,
                                 headers=headers)

    filter_info = {'filter_key': 'id', 'filter_value': ['object_url']}
    return req_util(tagging_resp, Response, filter_fields=['content'], filter_info=filter_info)
