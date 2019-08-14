# -*- coding: utf-8 -*-
# cdn配置 上传地址
endpoint = "http://oss-cn-beijing.aliyuncs.com"
# todo 这个地址是要配置变更的 下载地址
get_endpoint = "http://product-cdn-tagging.oss-cn-beijing.aliyuncs.com"
accessKeyId = "LTAIxsXYYXGS4eSg"
accessKeySecret = "cFUWZ3DQSk9BcsQnOAKubljTBy7nzL"
bucketName = "product-cdn-tagging"

TEST_TASK_BASE = 'test_base'
USER_ALIPAY_BASE = 'user_alipay'


def gen_pic_upload_folder(now):
    # from util.get_config import get_config
    get_config = {}
    tmp_path = get_config("upload", "PIC_UPLOAD_FOLDER")
    tmp_path = tmp_path.replace('yyyy', str(now.year))
    tmp_path = tmp_path.replace('mm', str(now.month))
    tmp_path = tmp_path.replace('MM', str(now.month))
    tmp_path = tmp_path.replace('dd', str(now.day))
    return tmp_path

# def gen_id_card_folder(now):
#     # from util.get_config import get_config
#     get_config = {}
#     tmp_path = get_config("upload", "ID_CARD_UPLOAD_FOLDER")
#     tmp_path = tmp_path.replace('yyyy', str(now.year))
#     tmp_path = tmp_path.replace('mm', str(now.month))
#     tmp_path = tmp_path.replace('MM', str(now.month))
#     tmp_path = tmp_path.replace('dd', str(now.day))
#     return tmp_path

# def gen_common_folder(now):
#     # REQUIREMENT_DOC
#     # from util.get_config import get_config
#     get_config = {}
#     tmp_path = get_config("upload", "COMMON_UPLOAD_FOLDER")
#     return tmp_path
