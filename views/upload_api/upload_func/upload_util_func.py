# -*- coding: utf-8 -*-
import os
import oss2
import json
import shutil
import validators
import hashlib
import requests

from PIL import Image
from datetime import datetime
from flask_babel import _
from config import Logger
from flask_login import current_user
from flask import jsonify, current_app

from app import xredis
from util.get_config import get_config
from .const import UPLOAD_TMP_FILE, UPLOAD_TMP_URLS, UPLOAD_TMP_BATCH_URLS, \
    UPLOAD_TMP_URLS_INDEX
# from util.tasks import task_add
from util.public import date2str
from config.upload_config import TEST_TASK_BASE, accessKeyId, accessKeySecret, \
                                 endpoint, bucketName, USER_ALIPAY_BASE, \
                                 get_endpoint, gen_pic_upload_folder
                                 # gen_id_card_folder, gen_common_folder
from config.error_code import NOT_UPLOAD_TASK_NAME, FILENAME_FAILED, \
                              FILE_EXT_FAILED, FILE_TOO_BIG, MAX_IMG_LENGTH, \
                              FILE_LINE_ERROR, FILE_NOT_EXIST, DATA_NOT_FOUND,\
                              UPLOAD_TYPE_ERROR, PARAMS_NOT_PROVIDED, \
                              OPERATOR_ERROR, NOT_UPLOAD_FILE

from models import Task

# todo 有关以后的扩展
# todo 上传至本地文件/本地文件开接口.

def getSize(fileobject):
    fileobject.seek(0,2) # move the cursor to the end of the file
    size = fileobject.tell()
    return size


def check_name(filename):
    """检查名称是否合法"""

    set_str = set(['#', '?'])
    set_filename = set(filename)
    if set_str & set_filename:
        return False, jsonify(code=1005, msg='名称非法, 文件名不能含有 # ？')
    else:
        return True, jsonify(code=200, msg='successful')

# def error_rollback(file_paths):
#     """批量上传失败, 回退, 删除之前上传的文件"""
#     for path in file_paths:
#         os.remove(path)

# def check_file_exist(base_path, file_names):
#     """检查路径下, 文件是否全部存在"""
#     for name in file_names:
#         if not os.path.exists(os.path.join(base_path, name)):
#             return False
#     return True

# def delete_not_exist_file(base_path, file_names):
#     """删除路径下, 文件列表外文件"""
#     for filename in os.listdir(base_path):
#         if filename not in file_names:
#             os.remove(os.path.join(base_path, filename))


def get_local_tmp_path(up_type, project_id=None, requirement_id=None):
    """生成本地临时存放路径"""
    base_path = None
    if up_type == "project":
        base_path = '{0}/{1}/{2}/{3}'.format(current_app.root_path,
                                             get_config("task", "PROJECT_FILE_PATH"),
                                             project_id,
                                             "tmp")
    if up_type == "requirement":
        base_path = '{0}/{1}/{2}/{3}'.format(current_app.root_path,
                                             get_config("task", "REQUIREMENT_FILE_PATH"),
                                             requirement_id,
                                             "tmp")

    # 存放未确认文件, 临时路径
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    return base_path

def get_upload_file_type():
    return ['jpg', 'png', 'jpeg'], \
           ['txt', 'json', 'csv'], \
           ['zip', 'rar'], None


def save_ret_img_md5(fd_in, save_path):
    import hashlib
    f_image = Image.open(fd_in)
    f_image.save(save_path)
    igm = open(save_path, 'rb')
    fmd5 = hashlib.md5(igm.read())
    igm.close()
    return fmd5.hexdigest()

def save_ret_file_md5(fd_in, save_path):
    fd_in.save(save_path)
    fd = open(save_path, 'rb')
    md5_obj = hashlib.md5()
    md5_obj.update(fd.read())
    md5_code = md5_obj.hexdigest()
    fd.close()
    return str(md5_code).lower()

def check_img_format(save_path):
    f_image_size = os.path.getsize(save_path)
    if f_image_size > (10 * 1024 * 1024):
        return False
    return True

def check_file_format(save_path, upload_tmp_url, upload_tmp_url_index):

    # 内容是否合法, 文件行数限制.
    object_urls = []
    error_urls = []
    repeat_urls = []
    with open(save_path) as fd:
        img_type, _, _, _ = get_upload_file_type()
        lines = fd.readlines()
        line_num = len(lines)
        if line_num > 100000:
            error_urls.append({"file": save_path, "msg": '文件超过100000行'})
            return False, object_urls, error_urls, repeat_urls

    read_num = 1
    file_type = save_path.split('.')[-1]
    if file_type == "json":
        for line in lines:
            read_num += 1
            if isinstance(line, bytes):
                line = line.decode()
            line = line.strip('\n').strip('\r')
            try:
                line = json.loads(line)
            except Exception as e:
                error_urls.append({"file": save_path,
                                   "msg" :('格式校验失败, 第%s行' % read_num)})
                continue
            if "pre_data" not in line or "object_url" not in line:
                error_urls.append({"file": save_path,
                                   "msg" :('属性缺失, 第%s行' % read_num)})
                continue

            object_url = line["object_url"]
            pre_data = line["pre_data"]
            object_type = line.get("object_type", "img")

            # img_text, text 类型使用.
            object_text = line.get("object_text")
            object_path = line.get("object_path")

            if object_type not in ("img", "img_text", "text", "tracking"):
                error_urls.append({"file": save_path,
                                    "msg": ('指定类型错误, 第%s行' % read_num)})
                continue

            if object_type in ("img", "img_text"):
                if validators.url(object_url) is True:
                    line_ext = object_url.rsplit('.')[-1]
                    if line_ext.lower() not in img_type:
                        error_urls.append({"file": save_path,
                                           "msg": ('图片格式不合格, 第%s行' % read_num)})
                        continue
                else:
                    error_urls.append({"file": save_path,
                                       "msg": ('图片url错误, 第%s行' % read_num)})
                    continue
                object_key = object_url
            if object_type == "text":
                object_key = object_text

            if object_type == "tracking":
                # tracking object_url 为路径+多图片. dict结构
                object_key = str(object_url)


            l_list = {"object_type": object_type, "object_url": str(object_url),
                      "object_text": object_text, "object_key": object_key}
            if xredis.hexists(upload_tmp_url, object_key):
                repeat_urls.append(object_key)
            else:
                xredis.lpush(upload_tmp_url_index, str(l_list))
                xredis.hset(upload_tmp_url, object_key, str(line))
                object_urls.append(object_key)

    if file_type == "txt":
        for line in lines:
            object_url = line
            read_num += 1
            if validators.url(object_url) is True:
                line_ext = object_url.rsplit('.')[-1]
                if line_ext.lower() not in img_type:
                    error_urls.append({"file": save_path,
                                       "msg": ('图片格式不合格, 第%s行' % read_num)})
                    continue
            else:
                error_urls.append({"file": save_path,
                                   "msg": ('图片url错误, 第%s行' % read_num)})
                continue

            d_url = {"object_type": "img", "object_url": object_url}
            l_list = {"object_type": "img", "object_url": object_url,
                      "object_text": "", "object_key": object_url}
            if xredis.hexists(upload_tmp_url, object_url):
                repeat_urls.append(object_url)
            else:
                xredis.lpush(upload_tmp_url_index, l_list)
                xredis.hset(upload_tmp_url, object_url, str(d_url))
                object_urls.append(object_url)
    return True, object_urls, error_urls, repeat_urls

# def statistics_task_nums(real_dir):
#     """统计任务数"""
#     nums = 0
#     img_type, file_type, compress_type, _ = get_upload_file_type()
#     for filename in os.listdir(real_dir):
#         ext = filename.split(".")[-1]
#         if ext in img_type:
#             nums += 1
#
#         if ext in file_type:
#             with open(os.path.join(real_dir, filename)) as f:
#                 nums += len(f.readlines())
#
#         if ext in compress_type:
#             pass
#
#     return nums

def publish_task(project_id, obj_info):
    """发布任务数量, 异步任务回写"""
    # 同步至数据库.
    # 更新obj_info信息. object_url='', object_text=''

    pos_obj_info = {}
    Logger.error(obj_info)
    for key, info in obj_info.items():
        info = eval(info)
        info["object_url"] = ''
        info["object_text"] = ''
        pos_obj_info[key] = str(info)

    from flask import request
    from config.config import VERSION, BASE_API_URL
    headers = {'Referer': 'http://127.0.0.1:8008/66635'}
    base_url = BASE_API_URL + VERSION
    url = os.path.join(base_url, 'upload/add_task')
    res = requests.post(url=url,
                        cookies=request.cookies,
                        json={"project_id":project_id, "objects_info": pos_obj_info},
                        headers=headers)
    print('-----------------------------------')
    content = eval(res.text)
    data = content.get('data')
    print('data',data)
    for task_id, obj_url in zip(data, obj_info.values()):
        obj_url = eval(obj_url)
        Task.create(**{
            "task_id": task_id,
            "object_url": obj_url.get("object_url", "")
        })



def uploaded_check(uploaded_files, req_form):
    """
    上传文件
    成功数, 失败数, 错误数.
    """

    req_dict = req_form.to_dict()
    up_type = req_dict.get("upload_type")
    project_id = req_dict.get("project_id")
    requirement_id = req_dict.get("requirement_id")

    # 判断需求状态是否允许上传
    # task = PlatformTask.get_instance(requirement_id)
    # status_list = LocalStatus.query.filter_by(category="task").all()
    # accept_status = [item.id for item in status_list if item.en_name in ("active", "nonactivated")]
    #
    # if requirement_id:
    #     if not task:
    #         return jsonify(code=PARAMS_NOT_PROVIDED, msg="无效的需求id")
    #     if task.status not in accept_status:
    #         return jsonify(code=DATA_NOT_FOUND, msg="需求状态, 不允许上传文件")
    #     if task.creator_id != current_user.id:
    #         return jsonify(code=OPERATOR_ERROR, msg="操作非法")
    #     local_status = LocalStatus.query.filter_by(category='task', name='delete').first()
    #     if task.status == local_status:
    #         return jsonify(code=OPERATOR_ERROR, msg="需求已删除")
    #
    # if project_id:
    #     project = Project.get_instance(project_id)
    #     if not project:
    #         return jsonify(code=PARAMS_NOT_PROVIDED, msg="无效的参数")
    #     if current_user.platform != project.platform:
    #         return jsonify(code=OPERATOR_ERROR, msg="非法操作")

    req_dict["check_type"] = "uploaded_check"
    # res = requests.post("check", json=req_dict)

    # 文件缓存隔离级别为: 单个项目/需求, 每一次上传.
    # 合法检查
    from flask import request
    from config.config import VERSION, BASE_API_URL
    headers = {'Referer': 'http://127.0.0.1:8008/66635'}
    # api_url = request.base_url.split(VERSION)[-1]
    base_url = BASE_API_URL + VERSION
    url = os.path.join(base_url, 'upload/check_legal')
    res = requests.post(url=url, cookies=request.cookies, json=req_dict, headers=headers)
    print('-----------------------------------')
    print(res.text, type(res.text))
    print('-----------------------------------')
    res_json = json.loads(res.text)
    if res_json.get("code") != 200:
        return res

    upload_tmp_file = UPLOAD_TMP_FILE.format(up_type=up_type,
                                             id=(project_id or requirement_id))
    upload_tmp_url = UPLOAD_TMP_URLS.format(up_type=up_type,
                                            id=(project_id or requirement_id))
    upload_tmp_url_index = UPLOAD_TMP_URLS_INDEX.format(up_type=up_type,
                                                        id=(project_id or requirement_id))

    # 图片临时存放位置
    local_tmp_path = get_local_tmp_path(up_type, project_id, requirement_id)
    # 文件合法格式
    img_type, file_type, compress_type, _ = get_upload_file_type()
    # 文件成功数, 失败数, 重复数.
    success_file_num, failure_file_num, repeat_file_num = 0, 0, 0
    error_content = []
    repeat_content = []
    for f in uploaded_files:
        file_name = f.filename
        _name, _type = os.path.splitext(file_name)
        ext = _type.strip('.').lower()

        # 名称检查
        is_legal, res_info = check_name(_name)
        if not is_legal:
            error_content.append({"file": file_name, "msg": '文件名称不合法'})
            Logger.error("%s 文件名称不合法" % file_name)
            failure_file_num += 1
            continue
        # 类型检查
        if ext not in (img_type + file_type + compress_type):
            error_content.append({"file": file_name, "msg": '文件后缀不合规'})
            Logger.error("%s 文件后缀不合规" % file_name)
            failure_file_num += 1
            continue

        file_info = xredis.hgetall(upload_tmp_file)
        # 重名检查
        if file_name in list(file_info.keys()):
            error_content.append({"file": file_name, "msg": '文件名重复'})
            Logger.error("%s 文件已存在, 文件名称重复" % file_name)
            repeat_file_num += 1
            continue

        # 存放路径.
        save_path = os.path.join(local_tmp_path, f.filename)
        # 保存文件, 计算md5值, 判断文件是否已存在
        if ext in img_type:
            md5_code = save_ret_img_md5(f, save_path)
        if ext in file_type:
            md5_code = save_ret_file_md5(f, save_path)


        if md5_code not in list(file_info.values()):
            xredis.hset(upload_tmp_file, file_name, md5_code)
        else:
            os.remove(save_path)
            error_content.append({"file": file_name, "msg": '文件已存在, 内容相同'})
            Logger.error("%s 文件已存在, 内容相同" % file_name)
            repeat_file_num += 1
            continue

        # 图片校验
        if ext in img_type:
            res = check_img_format(save_path)
            if res is False:
                os.remove(save_path)
                xredis.hdel(upload_tmp_file, file_name)
                Logger.error("%s 图片过大不合法" % file_name)
                failure_file_num += 1
                continue
            id_ = requirement_id or project_id
            cdn_path = get_cdn_path(req_dict={"upload_type": up_type,
                                              "id":id_},
                                    filename=file_name)
            with open(save_path, 'rb') as pic_f:
                upload_img(pic_f, cdn_path)
                cdn_info = {'object_url': cdn_path, 'object_type': "img"}
                xredis.hset(upload_tmp_url, cdn_path, str(cdn_info))
                l_list = {"object_type": "img", "object_url": cdn_path,
                          "object_text": "", "object_key": cdn_path}
                xredis.lpush(upload_tmp_url_index, str(l_list))

        # 文件校验
        if ext in file_type:
            res, _, error_urls, repeat_urls = check_file_format(save_path,
                                                                upload_tmp_url,
                                                                upload_tmp_url_index)
            if res is True:
                error_content.extend(error_urls)
                repeat_content.extend(repeat_urls)
                success_file_num += 1
            else:
                error_content.extend(error_urls)
                repeat_content.extend(repeat_urls)
                failure_file_num += 1
                xredis.hdel(upload_tmp_file, file_name)

    file_list = xredis.hgetall(upload_tmp_file)
    object_info = xredis.lrange(upload_tmp_url_index, 0 ,9)
    ret_info = []
    pos = 0
    for info in list(object_info):
        info = eval(info)
        object_type = info.get("object_type")
        if object_type in ("tracking", ):
            object_url = eval(info.get("object_url"))
            main = object_url.get("main", {})
            base_url = main.get("base_url", '')
            pic_1 = main.get("picture", [''])[0]
            object_url = os.path.join(base_url, pic_1)
            info["object_url"] = os.path.join(get_endpoint, object_url)
        else:
            object_url = info.get("object_url")
            if object_url and ("http" not in object_url):
                abs_url = "{0}/{1}".format(get_endpoint, object_url)
                info["object_url"] = abs_url
        info["id"] = pos
        pos += 1
        ret_info.append(info)
    total = xredis.llen(upload_tmp_url_index)
    data = {"file_list": list(file_list.keys()),
            "object_urls": ret_info,
            "error_content": error_content,
            "repeat_content": repeat_content,
            "success_file_num":success_file_num,
            "failure_file_num": failure_file_num,
            "repeat_file_num": repeat_file_num}
    # 设定缓存过期时间, 1小时.
    xredis.expire(upload_tmp_url, 60*60)
    xredis.expire(upload_tmp_url_index, 60*60)
    xredis.expire(upload_tmp_file, 60*60)
    return jsonify(code=200, msg= "文件上传成功", content={"data": data,
                                                         "total": total})

def confirm_process(req_json):
    """确认上传"""
    filename = req_json.get("file_name")

    upload_type = req_json.get("upload_type")
    project_id = req_json.get('project_id')
    requirement_id = req_json.get('requirement_id')
    # if upload_type == "requirement":
    #     obj = PlatformTask.get_instance(id_=requirement_id)
    #     if not obj:
    #         return jsonify(code=DATA_NOT_FOUND, msg="无效的需求id")
    #     if obj.creator_id != current_user.id:
    #         return jsonify(code=OPERATOR_ERROR, msg="非法操作")
    #
    # if upload_type == "project":
    #     obj = Project.get_instance(_id=project_id)
    #     if not obj:
    #         return jsonify(code=DATA_NOT_FOUND, msg="无效的项目id")
    #     if current_user.platform != obj.platform:
    #         return jsonify(code=OPERATOR_ERROR, msg="非法操作")


    # 合法检查
    upload_tmp_file = UPLOAD_TMP_FILE.format(up_type=upload_type,
                                             id=(project_id or requirement_id))
    upload_tmp_url = UPLOAD_TMP_URLS.format(up_type=upload_type,
                                            id=(project_id or requirement_id))
    upload_tmp_url_index = UPLOAD_TMP_URLS_INDEX.format(up_type=upload_type,
                                                        id=(project_id or
                                                            requirement_id))

    req_json["check_type"] = "confirm_process"
    req_json["counts"] = xredis.llen(upload_tmp_url_index)
    # res = requests.post("check", json=req_json)
    # res_json = json.loads(res.text())
    # if res_json.get("code") != 200:
    #     return res
    from flask import request
    from config.config import VERSION, BASE_API_URL
    headers = {'Referer': 'http://127.0.0.1:8008/66635'}
    # api_url = request.base_url.split(VERSION)[-1]
    base_url = BASE_API_URL + VERSION
    url = os.path.join(base_url, 'upload/check_legal')
    res = requests.post(url=url, cookies=request.cookies, json=req_json, headers=headers)
    print('-----------------------------------')
    print(res.text, type(res.text))
    print('-----------------------------------')
    res_json = json.loads(res.text)
    if res_json.get("code") != 200:
        return res


    local_path = get_local_tmp_path(upload_type, project_id, requirement_id)
    # 类型检查
    img_type, file_type, compress_type, _ = get_upload_file_type()
    # # 确认提交文件存在.
    # if not check_file_exist(local_path, filename):
    #    return jsonify(code=FILE_NOT_EXIST, msg='文件不存在')

    # # 删除不在指定名称列表内文件.
    # delete_not_exist_file(local_path, filename)
    base_dir = os.path.dirname(local_path)

    if upload_type == "requirement":
        # 生成批次, 重命名tmp文件
        # batch = ImgBatch.create(**{"desc": req_json.get("desc", ""),
        #                            "status": BatchImgStatus.WAITING_PUBLISH.value,
        #                            "img_list": "",
        #                            "requirement_id": requirement_id}
        #                             )

        # 更新批次数量
        # success_count = xredis.llen(upload_tmp_url_index)
        # batch.update(**{"counts": success_count})
        # 重命名tmp文件为批次id
        batch_id = res_json.get("data").get("batch_id")
        os.rename(local_path, os.path.join(base_dir, str(batch_id)))
        xredis.delete(upload_tmp_file)
        xredis.delete(upload_tmp_url_index)
        upload_tmp_batch_urls = UPLOAD_TMP_BATCH_URLS.format(up_type=upload_type,
                                                             id=(project_id or requirement_id),
                                                             batch_id=batch_id)
        xredis.rename(upload_tmp_url, upload_tmp_batch_urls)

    if upload_type == "project":
        try:
            obj_urls = xredis.hgetall(upload_tmp_url)
            publish_task(project_id, obj_urls)
            xredis.delete(upload_tmp_file)
            xredis.delete(upload_tmp_url)
            xredis.delete(upload_tmp_url_index)
        except Exception as e:
            Logger.error("发布任务异常 %s" % e)
            return jsonify(code=1, msg="发布任务异常")

        # 文件保存, 图片及压缩包删除.
        for name in filename:
            _type = name.split('.')[-1]
            if _type in file_type:
                os.rename(local_path,
                          os.path.join(base_dir, date2str(datetime.now())))

        if os.path.exists(local_path):
            shutil.rmtree(local_path)

    return jsonify(code=200, msg="确认成功")

def publish_batch(req_json):
    batch_id = req_json.get("img_batch_id")
    # batch_obj = ImgBatch.query.filter_by(id=batch_id).first()
    # if not batch_obj:
    #     return jsonify(code=PARAMS_NOT_PROVIDED, msg="无效的批次id")
    #
    # published_id = LocalStatus.query.filter_by(category="batch",
    #                                            en_name="published").first().id
    # if batch_obj.status == published_id:
    #     return jsonify(code=PARAMS_NOT_PROVIDED, msg="批次已发布")
    #
    # local_tmp_path = get_local_tmp_path("requirement", project_id=None,
    #                                      requirement_id=batch_obj.requirement_id)
    #
    # task = PlatformTask.get_instance(batch_obj.requirement_id)
    # if task.creator_id != current_user.id:
    #     return jsonify(code=OPERATOR_ERROR, msg="操作非法")
    #
    # active_status = LocalStatus.query.filter_by(category="task",
    #                                             name="active").first()
    # if task.status != active_status.id:
    #     return jsonify(code=PARAMS_NOT_PROVIDED, msg="需求未审核通过, 不允许发布")
    #
    # # 需求已发布项目, 更改批次状态为发布.
    # if batch_obj.project_id:
    #     batch_obj.update(**{"status": published_id})
    #     return jsonify(code=200, msg="更新状态成功")
    #
    # # 创建项目
    # protect_status = LocalStatus.query.filter_by(category="project",
    #                                              name="protect").first()
    # if not current_user.platform:
    #     platform = User.query.filter(User.id==current_user.id).first().platform
    # else:
    #     platform = current_user.platform
    # request.json["name"] = task.name  # 项目名称
    # request.json["status"] = protect_status.id  # 项目状态 默认保护
    # request.json["finish_time"] = date2str(datetime.now() + timedelta(7))
    # request.json["requirement_name"] = task.creator.username or task.creator.email
    # request.json["batch_id"] = batch_obj.id
    # request.json["temp_id"] = task.temp_id
    # request.json["platform"] = platform
    # request.json["demand_user_id"] = current_user.id
    #
    # del request.json["img_batch_id"]

    # 创建项目
    # pro_obj = sql_create(Project, ProjectCreateForm)  # 同步执行.
    #
    # data = json.loads(pro_obj.data)
    # project_id = data["data"]["id"]
    #
    # active_status = LocalStatus.query.filter_by(category="batch",
    #                                             name="published").first()
    # batch_obj.update(**{"project_id": project_id, "status": active_status.id})
    req_json["check_type"] = "publish_batch"
    res = requests.post("check", json=req_json)
    res_json = json.loads(res.text())
    if res_json.get("code") != 200:
        return res
    try:
        project_id = res_json.get("data").get("project_id")
        requirement_id = res_json.get("data").get("requirement_id")
        upload_tmp_batch_url = UPLOAD_TMP_BATCH_URLS.format(up_type="requirement",
                                                            id=requirement_id,
                                                            batch_id=batch_id)
        obj_urls = xredis.hgetall(upload_tmp_batch_url)
        publish_task(project_id, obj_urls)
        xredis.delete(upload_tmp_batch_url)
    except Exception as e:
        Logger.error("发布任务异常 %s" % e)
        return jsonify(code=1, msg="发布任务异常")
    return jsonify(code=200, msg="批次发布成功")

def get_cdn_path(req_dict, filename):
    """
    返回cdn地址.
    """
    upload_type = req_dict.get('upload_type', "test_task")
    category_id = req_dict.get('id')
    if not category_id:
       return jsonify(code=NOT_UPLOAD_TASK_NAME, msg= '未传分类id')

    now = datetime.now()
    # if upload_type == "test_task":
    #     test_task = TestTask.query.filter_by(id=category_id).first()
    #     if not test_task:
    #         return '', jsonify(code=NOT_UPLOAD_TASK_NAME, msg=_('测试项目不存在'))
    #     cdn_file_path = TEST_TASK_BASE + datetime.now().strftime('%Y-%m') + '/%s/%s' % (category_id, filename)
    #     return cdn_file_path
    if upload_type == "project":
        cdn_file_path = gen_pic_upload_folder(now)  + '/%s/%s' % (category_id, filename)
        return cdn_file_path
    elif upload_type == "requirement":
        cdn_file_path = gen_pic_upload_folder(now)  + '/%s/%s' % (category_id, filename)
        return cdn_file_path
    # elif upload_type == "identity_card":
    #     cdn_file_path = gen_id_card_folder(now) + '/%s/%s' % (category_id, filename)
    #     return cdn_file_path
    # elif upload_type == "requirement_doc":
    #     time_now = datetime.now()
    #     name, ext = filename.split('.')
    #     filename = '.'.join([name +'_'+ str(int(time_now.timestamp())),ext])
    #     cdn_file_path = '/'.join([gen_common_folder(now), filename])
    #     return cdn_file_path
    # elif upload_type == "platform_logo":
    #     time_now = datetime.now()
    #     name, ext = filename.split('.')
    #     filename = '.'.join([name + '_' + str(int(time_now.timestamp())), ext])
    #     cdn_file_path = '/'.join([gen_common_folder(now), 'platform_logo',
    #                               filename])
    #     return cdn_file_path
    # else:
    else:
        return None

def upload_img(picture, cdn_path):
    auth = oss2.Auth(accessKeyId, accessKeySecret)
    bucket = oss2.Bucket(auth, endpoint, bucketName)

    if not bucket.object_exists(cdn_path):
        bucket.put_object(cdn_path, picture.read())

def delete_cnd_path(cdn_path):
    auth = oss2.Auth(accessKeyId, accessKeySecret)
    bucket = oss2.Bucket(auth, endpoint, bucketName)

    if bucket.object_exists(cdn_path):
        bucket.delete_object(cdn_path)
        return True
    return False

# 测试任务上传图片
# def test_task_start_upload(req_file, req_form):
#
#     # 测试任务当前是每次上传都请求.
#     req_file = req_file[0]
#     filename, ext = os.path.splitext(req_file.filename)
#
#     res, info = check_name(filename)
#     if res is False:
#         return info
#
#     req_dict = req_form.to_dict()
#     req_dict["id"] = req_dict["task_id"]
#     save_path = get_cdn_path(req_dict, req_file.filename)
#     if save_path is None:
#         return jsonify(code=DATA_NOT_FOUND, msg=_('上传类型错误'))
#
#     if ext.strip('.').lower() in ['jpg', 'png']:
#         upload_img(req_file, save_path)
#         return jsonify(code=200,
#                        msg=_('成功'),
#                        file_path=save_path,
#                        path=save_path)
#     else:
#         return jsonify(code=UPLOAD_TYPE_ERROR, msg=_('上传类型错误'))

# 实名认证上传图片
# def identity_card_start_upload(req_file, req_form):
#
#     # 测试任务当前是每次上传都请求.
#     req_file = req_file[0]
#     filename, ext = os.path.splitext(req_file.filename)
#
#     res, info = check_name(filename)
#     if res is False:
#         return info
#
#     from flask_login import current_user
#     req_dict = req_form.to_dict()
#     req_dict["id"] = current_user.id
#
#     save_path = get_cdn_path(req_dict, req_file.filename)
#     if save_path is None:
#         return jsonify(code=DATA_NOT_FOUND, msg=_('上传类型错误'))
#
#     if ext.strip('.').lower() in ['jpg', 'png']:
#         upload_img(req_file, save_path)
#         return jsonify(code=200,
#                        msg=_('成功'),
#                        file_path=os.path.join(get_endpoint, save_path),
#                        path=save_path)
#     else:
#         return jsonify(code=UPLOAD_TYPE_ERROR, msg=_('上传类型错误'))
# 需求文档上传
# def requirement_doc_start_upload(req_files, req_form):
#
#     # 测试任务当前是每次上传都请求.
#     for req_file in req_files:
#         # 文档大小限制
#         byte_size = int(request.headers.get('Content-Length', 0))
#         if byte_size/(1024*1024) > 20:
#             return jsonify(code=FILE_TOO_BIG, msg=_('文件大小超限制20m'))
#         filename, ext = os.path.splitext(req_file.filename)
#         # 中文名称也可以.
#         res, info = check_name(filename)
#         if res is False:
#             return info
#
#         from flask_login import current_user
#         cdn_dict = {}
#         cdn_dict["id"] = current_user.id
#         cdn_dict["upload_type"] = "requirement_doc"
#
#         save_path = get_cdn_path(cdn_dict, req_file.filename)
#         if save_path is None:
#             return jsonify(code=DATA_NOT_FOUND, msg=_('生成cdn服务器地址失败'))
#
#         if ext.strip('.').lower() in ['doc', 'docx', 'txt', 'pdf', 'xls', 'xlsx']:
#             upload_img(req_file, save_path)
#             return jsonify(code=200,
#                            msg=_('成功'),
#                            file_path=os.path.join(get_endpoint, save_path),
#                            path=save_path)
#         else:
#             return jsonify(code=UPLOAD_TYPE_ERROR, msg=_('上传类型错误'))

# 创建平台logo上传
# def platform_logo_start_upload(req_file, req_form):
#
#     # 测试任务当前是每次上传都请求.
#     req_file = req_file[0]
#     filename, ext = os.path.splitext(req_file.filename)
#
#     res, info = check_name(filename)
#     if res is False:
#         return info
#
#     from flask_login import current_user
#     req_dict = req_form.to_dict()
#     req_dict["id"] = current_user.id
#
#     save_path = get_cdn_path(req_dict, req_file.filename)
#     if save_path is None:
#         return jsonify(code=DATA_NOT_FOUND, msg=_('上传类型错误'))
#
#     if ext.strip('.').lower() in ['jpg', 'png']:
#         upload_img(req_file, save_path)
#         return jsonify(code=200,
#                        msg=_('成功'),
#                        file_path=os.path.join(get_endpoint, save_path),
#                        path=save_path)
#     else:
#         return jsonify(code=UPLOAD_TYPE_ERROR, msg=_('上传类型错误'))
# todo 上传类型不同转接/转接到远端服务器.
# 上传接口添加权限控制.
def upload_controller(req_file, req_form):
    req_dict = req_form.to_dict()
    if req_dict.get("upload_type") in ("project", "requirement"):
        # if current_user.role_id not in (142, 141, 104):
        #     return jsonify(code=OPERATOR_ERROR, msg="操作非法")
        return uploaded_check(req_file, req_form)
    # elif req_dict.get("upload_type") in ("test_task",):
    #     return test_task_start_upload(req_file, req_form)
    # elif req_dict.get("upload_type") in ("identity_card",):
    #     return identity_card_start_upload(req_file, req_form)
    # elif req_dict.get("upload_type") in ("requirement_doc",):
    #     if current_user.role_id not in (142, 141, 104):
    #         return jsonify(code=OPERATOR_ERROR, msg="操作非法")
    #     return requirement_doc_start_upload(req_file, req_form)
    # elif req_dict.get("upload_type") in ("platform_logo",):
    #     if current_user.role_id not in (104,):
    #         return jsonify(code=OPERATOR_ERROR, msg="操作非法")
    #     return platform_logo_start_upload(req_file, req_form)
    else:
        jsonify(code=UPLOAD_TYPE_ERROR, msg=_('上传类型错误'))

def upload_page(req_json):
    up_type = req_json.get("upload_type")
    project_id = req_json.get("project_id")
    requirement_id = req_json.get("requirement_id")
    page = int(req_json.get("page", 1))
    per_page = int(req_json.get("per_page",10))
    # if requirement_id:
    #     task = PlatformTask.get_instance(requirement_id)
    #     if not task:
    #         return jsonify(code=PARAMS_NOT_PROVIDED, msg="无效的参数")
    #     if task.creator_id != current_user.id:
    #         return jsonify(code=OPERATOR_ERROR, msg="非法操作")
    #
    #     local_status = LocalStatus.query.filter_by(category='task', name='delete').first()
    #     if task.status == local_status.id:
    #         return jsonify(code=OPERATOR_ERROR, msg="需求已删除")
    #
    # if project_id:
    #     project = Project.get_instance(project_id)
    #     if not project:
    #         return jsonify(code=PARAMS_NOT_PROVIDED, msg="无效的参数")
    #     if current_user.platform != project.platform:
    #         return jsonify(code=OPERATOR_ERROR, msg="非法操作")
    req_json["check_type"] = "upload_page"

    from flask import request
    from config.config import VERSION, BASE_API_URL
    headers = {'Referer': 'http://127.0.0.1:8008/15'}
    base_url = BASE_API_URL + VERSION
    url = os.path.join(base_url, 'upload/check_legal')
    res = requests.post(url=url, cookies=request.cookies, json=req_json, headers=headers)
    print('-----------------------------------')
    print(res.text, type(res.text))
    print('-----------------------------------')
    res_json = json.loads(res.text)
    if res_json.get("code") != 200:
        return res

    upload_tmp_url_index = UPLOAD_TMP_URLS_INDEX.format(up_type=up_type,
                                                        id=(project_id or requirement_id))
    object_info = xredis.lrange(upload_tmp_url_index,
                               (page-1)*per_page, page*per_page -1)
    total = xredis.llen(upload_tmp_url_index)
    ret_info = []
    pos = (page-1)*per_page
    for info in list(object_info):
        info = eval(info)
        object_type = info.get("object_type")
        if object_type in ("tracking", ):
            object_url = eval(info.get("object_url"))
            main = object_url.get("main", {})
            base_url = main.get("base_url", '')
            pic_1 = main.get("picture", [''])[0]
            object_url = os.path.join(base_url, pic_1)
            info["object_url"] = os.path.join(get_endpoint, object_url)
        else:
            object_url = info.get("object_url")
            if object_url and ("http" not in object_url):
                abs_url = "{0}/{1}".format(get_endpoint, object_url)
                info["object_url"] = abs_url
        info["id"] = pos
        pos += 1
        ret_info.append(info)
    return jsonify(code=200, data=ret_info, total=total)

def delete_path(req_json):
    up_type = req_json.get("upload_type")
    project_id = req_json.get("project_id")
    requirement_id = req_json.get("requirement_id")
    obj_ids = req_json.get("ids")
    if not obj_ids or not up_type:
        return jsonify(code=DATA_NOT_FOUND, msg="参数错误")

    upload_tmp_file = UPLOAD_TMP_FILE.format(up_type=up_type,
                                             id=(project_id or requirement_id))
    upload_tmp_url = UPLOAD_TMP_URLS.format(up_type=up_type,
                                            id=(project_id or requirement_id))
    upload_tmp_url_index = UPLOAD_TMP_URLS_INDEX.format(up_type=up_type,
                                                        id=(project_id or requirement_id))
    pre_delete_info = []
    for index in obj_ids:
        if xredis.exists(upload_tmp_url_index):
            pre_info = xredis.lindex(upload_tmp_url_index, index)
            pre_delete_info.append(pre_info)
            info = eval(pre_info)
            # 删除任务信息
            object_key = info.get("object_key")
            if xredis.exists(upload_tmp_url):
                xredis.hdel(upload_tmp_url, object_key)
            # 删除本地及上传文件
            object_url = info.get("object_url")
            if object_url and 'http' not in object_url:
                file_name = object_url.split('/')[-1]
                if xredis.exists(upload_tmp_file):
                    xredis.hdel(upload_tmp_file, file_name)
                    delete_cnd_path(object_url)
    # 删除index信息
    for pre_info in pre_delete_info:
        _ = xredis.lrem(upload_tmp_url_index, 1, pre_info)
    return jsonify(code=200, msg="删除成功")

