# -*- coding: utf-8 -*-
import os


from flask import jsonify
from flask_babel import _
from views.upload_api.upload_func.upload_util_func import \
    confirm_process, upload_controller, publish_batch, delete_cnd_path, \
    upload_page, delete_path


from config.error_code import NOT_UPLOAD_FILE

"""
    摘要:
        1. 文件类型: 图片(png, jpg), 可访问路径地址文件(txt, csv), 压缩文件(图片).
        2. 上传文件(存放在temp文件夹下), 确认上传文件.(使用temp下文件新建任务).
        
    注意:
        1. 文件类型中, 只需要保存txt文件即可.
        2. 是否使用阿里云, 最好做成插件化, 可配置的.
    
    问题: 
        1. 同一个项目多次上传时的文件保存问题?
        2. 尽量减少IO.
        3. 前端应该控制一下, 提交文件的大小.
        4. 如果再有其他的上传使用此接口该怎么办呢. +1 上传 upload_type 区分.
        
    补充:
        1. 未发现上传文件
        2. 上传图片数量超出限制
        3. 文件超过1000行
        4. 文件内容不合法
"""


class UploadController(object):
    @classmethod
    def start_upload(cls, req_file, req_form):
        uploaded_files = req_file.getlist("files")
        if not uploaded_files:
            return jsonify(code=NOT_UPLOAD_FILE, msg=_("上传文件不存在"))
        return upload_controller(uploaded_files, req_form)
    @classmethod
    def upload_page(cls, req_json):
        return upload_page(req_json)

    @classmethod
    def delete_path(cls, req_json):
        return delete_path(req_json)

    @classmethod
    def confirm_upload(cls, req_json):
        return confirm_process(req_json)

    @classmethod
    def publish_batch(cls, req_json):
        return publish_batch(req_json)

    # @classmethod
    # def delete_cdn_path(cls, req_json):
    #     cdn_path = req_json.get("path")
    #     requirement_id = req_json.get("requirement_id")
    #     platform_id = req_json.get("platform_id")
    #     if cdn_path:
    #         # 删除需求文档
    #         if requirement_id:
    #             task= PlatformTask.get_instance(id_=requirement_id)
    #             task.update(**{"upload_doc_url": ""})
    #         # 删除平台logo
    #         if platform_id:
    #             platform = Platform.get_instance(id_=platform_id)
    #             platform.update(**{"url_logo": ""})
    #
    #         if delete_cnd_path(cdn_path):
    #             return jsonify(code=200, msg=_("删除成功"))
    #     return jsonify(code=NOT_UPLOAD_FILE, msg=_("删除的文件不存在"))