import json

import requests
from flask import request, jsonify
from config.config import VERSION, BASE_API_URL
from app import app




from views.response import response_bp
app.register_blueprint(response_bp, url_prefix='')



@app.after_request
def after_request(response):
    headers = {'Referer': 'http://127.0.0.1:8008/66635'}
    api_url = request.base_url.split(VERSION)[-1]
    if api_url  == '/login':
        url = BASE_API_URL + VERSION + api_url
        resp = requests.post(url=url, cookies=request.cookies, data=request.form,
                             headers=headers)
        resp_data = json.loads(resp.content)

        return jsonify(resp_data)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009)