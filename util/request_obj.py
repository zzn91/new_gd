from flask import request

from config.config import VERSION, BASE_API_URL


def get_url():
    api_url = request.base_url.split(VERSION)[-1]

    base_url = BASE_API_URL + VERSION
    url = base_url + api_url

    return url


def get_headers():
    headers = {'Referer': request.headers.get('Referer')}

    return headers