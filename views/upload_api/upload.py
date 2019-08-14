# -*- coding: utf-8 -*-

from flask import Blueprint, request

from config import Logger
from views.upload_api.upload_func.upload_func import UploadController
# from util.verify_perm import verify_perm

upload_bp = Blueprint('upload', __name__)

"""
整个接口应该只剩下与上传文件生成. 任务相关的
其他上传应该剔除掉.
"""

# todo  保留.
@upload_bp.route('/upload/uploads', methods=['POST'])
# @verify_perm(code='upload_uploads')
def upload_func():
    """
    ***文件上传***
    
    ***可以根据upload_type 进行逻辑判断.***

    *** 路径 /api/v1.0.0/upload/uploads***
    :
        path: ""

    **参数 body.from-data**
    :   
        upload_type:  project # 上传类型
        project_id: 100 # 项目id
        requirement_id: 8 # 需求id
        files: binary_file # 上传文件
        file_type: png
    **返回值 **
    :
        {
            "code": 200,
            "msg": "处理中"
        }
    """

    try:
        req_dict = request.form.to_dict()
        if req_dict.get("upload_type") in ("project", "requirement"):
            res = UploadController.start_upload(request.files, request.form)
        else:
            # 转接至远端服务器.
            pass
    except Exception as e:
        Logger.error(e)
    return res


# todo  保留.
@upload_bp.route('/upload/upload_confirm', methods=['POST'])
def upload_confirm():
    """
    ***确认上传***

    *** 路径 ***
    :
        path: "/api/v1.0.0/upload/upload_confirm"

    **参数 request.json**
    :   {
            upload_type: requirement
            project_id: 100 # 项目id
            requirement_id: 8 # 需求id
            file_name: [name, name, name, ..., name]
        }
    **返回值 **
    :
        {
            "code": 200,
            "msg": "处理中"
        }
    """
    from config import Logger
    try:
        res = UploadController.confirm_upload(request.json)
    except Exception as e:
        Logger.error(e)
    return res


# todo  保留.
@upload_bp.route('/upload/uploads/page', methods=['POST'])
# @verify_perm(code='upload_page')
def upload_page():
    """
    ***上传文件, 文件分页***

    ***可以根据upload_type 进行逻辑判断.***

    *** 路径 /api/v1.0.0/upload/uploads/page***
    :
        path: ""

    **参数 request.json**
    :   
        upload_type:  project # 上传类型
        project_id: 100 # 项目id
        requirement_id: 8 # 需求id
        page: 1
        per_page: 20
    **返回值 **
    :
        {
            "code": 200,
            "msg": "处理中"
        }
    """
    from config import Logger
    try:
        res = UploadController.upload_page(request.json)
    except Exception as e:
        Logger.error(e)
    return res

# todo  保留.
@upload_bp.route('/upload/uploads/delete_path', methods=['POST'])
# @verify_perm(code='upload_delete_path')
def delete_path():
    """
    ***删除路径***

    ***可以根据upload_type 进行逻辑判断.***

    *** 路径 /api/v1.0.0/upload/uploads/delete_path***
    :
        path: ""

    **参数 request.json**
    :   
        upload_type:  project # 上传类型
        project_id: 100 # 项目id
        requirement_id: 8 # 需求id
        obj_urls: []
    **返回值 **
    :
        {
            "code": 200,
            "msg": "处理成功"
        }
    """
    from config import Logger
    try:
        res = UploadController.delete_path(request.json)
    except Exception as e:
        Logger.error(e)
    return res

# # todo  保留.
# @upload_bp.route('/upload/upload_delete', methods=['POST'])
# @verify_perm(code='upload_delete_doc')
# def upload_delete():
#     """
#     ***上传(文档/logo)删除***
#
#     *** 路径 ***
#     :
#         path: "/api/v1.0.0/upload/upload_delete"
#
#     **参数 request.json**
#     :   {
#             path: "requirement_doc/2019/05/2275/状态码统计_1559202980.xls"
#             requirement_id: 100
#             platform_id:100
#         }
#     **返回值 **
#     :
#         {
#             "code": 200,
#             "msg": "处理中"
#         }
#     """
#     from config import  Logger
#     try:
#         res = UploadController.delete_cdn_path(request.json)
#     except Exception as e:
#         Logger.error(e)
#     return res