# -*- coding:utf-8 -*-
import json

from flask import jsonify


def req_util(resp, filter_obj, filter_fields=[], filter_info={},):
    if resp.status_code == 200:
        # try:
        resp_content = json.loads(resp.content)
        if resp_content.get('code') == 200:
            finally_resp = {}
            filter_key = filter_info.get('filter_key', '')

            filter_value = filter_info.get('filter_value', [])
            for k, v in resp_content.items():
                if k in filter_fields:
                    if k == 'content':
                        new_content = []
                        content = resp_content[k]
                        for ci in content:
                            print(ci)
                            new_ci = {}
                            field_ = eval(filter_info.get('field') % ci.get(filter_key))
                            obj = filter_obj.query.filter(field_).first()

                            for ci_k, ci_v in ci.items():
                                if ci_k in filter_value:
                                    if obj:
                                        new_ci[ci_k] = getattr(obj, ci_k)
                                        print(getattr(obj, ci_k))
                                else:
                                    new_ci[ci_k] = ci_v
                            new_content.append(new_ci)
                        finally_resp[k] = new_content
                else:
                    finally_resp[k] = v
            return jsonify(**finally_resp)
        else:
            return jsonify(**resp_content)
        # except Exception as e:
        #     return jsonify(code=444, msg=e)
    return resp
