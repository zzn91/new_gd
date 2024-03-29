# -*- coding: utf-8 -*-


PARAMS_NOT_PROVIDED = 10001  # 未传递参数
FORM_VALIDATE_ERROR = 10002  # 表单验证错误，msg返回{k:v, k:v}例: {'name': ['未填写任务名称'], 'type': ['未选择任务类型']}
DATA_NOT_FOUND = 10003
DATA_IS_EXISTS = 10004
DATA_OPERATION_ERROR = 1005  # 数据库操作错误
USER_NOT_LOGIN = 1006        # 用户未登录
CAN_NOT_DELETE = 10007       # 不可删除
CAN_NOT_DOWN = 10014         # 不可关闭
CAN_NOT_EDIT = 10008       # 不可修改
SYSTEM_IS_BUSY = 10009     # 系统繁忙
CAN_NOT_CREATE = 10012       # 不可创建
SETTING_CONTENT_NOT_OPTION = 10008 # 设置内容不在可选内
PARENT_PRESENCE_CANNOT_DELETE = 10009 # 父级存在无法删除
NOT_CHECK_COMPLETE = 10010   # 未质检完成
NOT_TEAM = 10011 # 没有团队
TEAM_NOT_CHECK=10013   # 当前团队不允许检查
SETTING_VALUE_ERROR = 10012  # 配置的参数错误
PROJECT_NOT_OPEN = 10014 # 项目不是开放状态
CURRENT_TEAM_DEFAULT = 10015  # 当前团队是默认团队
QUIT_TEAM_ROLE_ERROR = 10016  # 当前角色不能退出团队

# 上传文件
NOT_UPLOAD_FILE = 20001
NOT_UPLOAD_TASK_NAME = 20002
FILENAME_FAILED = 20003
FILE_EXT_FAILED = 20004
FILE_TOO_BIG = 20005
FILE_READ_ERROR = 20006
IMAGE_OPEN_FAILED = 20007
FILE_LINE_ERROR = 20008
MAX_IMG_LENGTH = 20009
IMG_DELETE_FAIL = 20010
UPLOAD_TYPE_ERROR = 20011
FILE_NOT_EXIST = 20011

# 金额
NOT_SUFFICIENT_FUNDS = 50001   # 余额不足

# 测试题
IMAGE_NOT_FOUND = 30001     # 图片格式不正确
BASE_TEST_PASS = 30002      # 已经通过基础测试
BASE_TEST_NOT_PASS = 30003  # 未通过基础测试
ANSWER_ERROR = 30004        # 回答错误
TEST_NOT_PASS = 30005       # 测试任务未通过
TEST_COMPLETE = 30006       # 测试任务已完成，等待管理员修改
NOT_BASE_TEST = 30007       # 暂无基础测试
BASE_TEST_NOT_CREATE = 30008 # 未创建基础测试，请先创建


# 回收
RESP_ALREADY_RECYCLE = 40001    # 回答已经回收

# 非法操作
OPERATOR_ERROR = 60001

# 下载错误
NOT_DOWNLOAD_PARAMS = 70001     # 未传下载参数
NOT_PROJECT_ID = 70002          # 未传项目ID
NOT_DOWNLOAD_TYPE = 70003       # 未传下载类型
DOWNLOAD_ERROR = 70004          # 下载失败
