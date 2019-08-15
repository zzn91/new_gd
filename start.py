import json

import requests
from flask import request, jsonify, g
from config.config import VERSION, BASE_API_URL
from app import app
from register_bp import register_bp
import time

register_bp(app)

local_path = ['/upload/uploads', '/upload/upload_confirm',
              '/upload/uploads/page', '/upload/uploads/delete_path']

@app.before_request
def before_request():
    g.time = time.time()

@app.after_request
def after_request(response):
    headers = {'Referer': 'http://127.0.0.1:8008/15'}
    api_url = request.base_url.split(VERSION)[-1]
    base_url = BASE_API_URL + VERSION
    if api_url == '/login':
        url = base_url + api_url
        resp = requests.post(url=url, cookies=request.cookies, data=request.form,
                             headers=headers)
        resp_data = json.loads(resp.content)

        return jsonify(resp_data)
    # the local path 需要本地处理的路径.
    elif api_url in local_path:
        pass
    else:
        url = base_url + api_url
        if request.method == 'POST':
            resp = requests.post(url=url, cookies=request.cookies, json=request.json,
                                 headers=headers)
        elif request.method == 'GET':
            resp = requests.get(url=url, cookies=request.cookies,headers=headers)

        resp_data = json.loads(resp.content)
        return jsonify(resp_data)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009)