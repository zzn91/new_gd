import json

import requests
from flask import request, jsonify, g
from werkzeug.routing import Rule

from config.config import VERSION, BASE_API_URL
from app import app
from register_bp import register_bp
import time

from util.request_obj import get_headers

register_bp(app)


@app.before_request
def before_request():
    g.time = time.time()
from views.response import response_bp
app.register_blueprint(response_bp, url_prefix=VERSION)



@app.after_request
def after_request(response):
    headers = get_headers()

    api_url = request.base_url.split(VERSION)[-1]
    base_url = BASE_API_URL + VERSION
    url = base_url + api_url

    for rule in app.url_map._rules:
        if isinstance(rule, Rule):
            rule_ = rule.rule.split(VERSION)[-1]

            if rule_ == api_url:
                return response

    if api_url == '/login':
        resp = requests.post(url=url, cookies=request.cookies, data=request.form,
                             headers=headers)
        resp_data = json.loads(resp.content)

        response = jsonify(resp_data)

        for k, v in resp.cookies.items():
            response.set_cookie(k, v)
        return response

    else:
        if request.method == 'POST':
            resp = requests.post(url=url, cookies=request.cookies, json=request.json,
                                 headers=headers)
        elif request.method == 'GET':
            resp = requests.get(url=url, cookies=request.cookies, headers=headers)
        else:
            return jsonify(code=404)

        resp_data = json.loads(resp.content)
        return jsonify(resp_data)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009)