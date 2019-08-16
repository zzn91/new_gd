import yaml
import logging

from logging import config as logging_config
# from config.new_config import config
# config = config.get('default')
DEBUG = True

__author__ = "Zhaozn"

"""
提供 API 日志服务功能
日志默认输出到程序运行当前目录下的 log 目录，系统自动创建目录结构
日志分为四个级别进行记录，分别是 info, error, warn, debug
"""

class Logger(object):

    def __init__(self):
        with open("./config/logging_conf.yaml", 'r') as fd:
                logging_config.dictConfig(yaml.safe_load(fd))
        self._warn = logging.getLogger('warn')
        self._debug = logging.getLogger('debug')
        self._info = logging.getLogger('info')
        self._error = logging.getLogger('error')

    def is_debug(self):
        if not DEBUG:
            self._warn.removeHandler('stream')
            self._debug.removeHandler('stream')
            self._info.removeHandler('stream')
            self._error.removeHandler('stream')

    def warn(self, msg):
        self._warn.warning(msg)

    def debug(self, msg):
        self._debug.debug(msg)

    def info(self, msg, resp=None):
        self._info.info(logger_info(msg, resp))

    def error(self, msg, resp=None, error=None):
        # exc_info 输出栈信息到错误日志中.
        self._error.error(logger_info(msg, resp, error), exc_info=True)


# 兼容之前的操作, 单例模式.
logger = Logger()
warn = logger.warn
debug = logger.debug
info = logger.info
error = logger.error
logger.is_debug()

# 删除初始化类.
del Logger

# 为什么把 nginx 的信息都往日志里放啊. 好奇怪. nginx 日志收集有问题么.
def logger_info(msg, resp=None, error=None):
    import time
    from flask import request, g
    path_time = str(time.time() - g.time)
    log_dict = {
        "url": request.base_url,
        "method": request.method,
        "site": request.url_root.split('//')[-1].split('.')[0],
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        'path_time': path_time[:5],
        "response": resp['response'] if resp else '',
        'msg': msg,
        "response_code": resp['resp_code'] if resp else '',
        "User-Agent": request.headers["User-Agent"],
    }
    if error:
        log_dict['error'] = error

    return log_dict
