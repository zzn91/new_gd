from flask import Blueprint
response_bp = Blueprint('user_bp', __name__)


def login():
    '''
    登陆
    :return:
    '''

def reset_password():
    '''
    重设密码
    :return:
    '''
    if request.method == 'GET':
        url = request.url.split('?')[-1]
        url = BASE_API_URL + '/reset?{}'.format(url)
        resp = requests.get(url=url, cookies=request.cookies)
        resp_data = json.loads(resp.content)
        if resp_data['code'] == 200:
            make_resp = make_response(render_template(resp_data['data'], language=g.language, la=g.la))
            for k, v in resp.cookies.items():
                make_resp.set_cookie(k, v)
            return make_resp
        else:
            return render_template('404.html', language=g.language, la=g.la)

    elif request.method == 'POST':
        url = BASE_API_URL + '/reset'
        resp = requests.post(url=url, cookies=request.cookies, data=request.form)
        resp_data = json.loads(resp.content)
        if resp_data['code'] == 1:
            return jsonify(resp_data)
    else:
        return render_template('404.html', language=g.language, la=g.la)