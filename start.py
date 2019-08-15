import json

import requests
from flask import request, jsonify, g
from werkzeug.routing import Rule

from config.config import VERSION, BASE_API_URL
from app import app


from views.response import response_bp
app.register_blueprint(response_bp, url_prefix=VERSION)



@app.after_request
def after_request(response):
    headers = {'Referer': 'http://127.0.0.1:8008/66635'}
    api_url = request.base_url.split(VERSION)[-1]
    base_url = BASE_API_URL + VERSION
    url = base_url + api_url

    for rule in app.url_map._rules:
        if isinstance(rule, Rule):
            if rule.rule in request.url:
                return response

    if api_url == '/login':
        resp = requests.post(url=url, cookies=request.cookies, data=request.form,
                             headers=headers)
        g.resp_cookies = resp.cookies
        resp_data = json.loads(resp.content)
        return jsonify(resp_data)
    else:
        if request.method == 'POST':
            resp = requests.post(url=url, cookies=request.cookies, json=request.json,
                                 headers=headers)
        elif request.method == 'GET':
            resp = requests.get(url=url, cookies=request.cookies,headers=headers)

        resp_data = json.loads(resp.content)
        return jsonify(resp_data)

@app.after_request
def after_request(response):
    '''
    请求返回，登陆时候把cookies放入response
    :param response:
    :return:
    '''
    cookies_ = g.get('resp_cookies', None)
    if cookies_:
        for k, v in cookies_.items():
            response.set_cookie(k, v)

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009)