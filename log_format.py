#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-1-7 下午5:05
# @Author  : ShaoXin
# @Summary :
# @Software: PyCharm
import logging
import logging.config
import cloghandler
import os

import tornado.log
from tornado.web import RequestHandler

prj_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
log_path = os.path.join(prj_dir, 'log')
if not os.path.exists(log_path):
    os.mkdir(log_path)
os.environ.setdefault('hr_log_path', os.path.join(log_path, 'code.log'))

log_ini_path = os.path.join(prj_dir, 'lib', 'config', 'logging.ini')


class LogFormatter(tornado.log.LogFormatter):
    """
    修改tornado默认输出日志格式
    """
    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(log_id)s %(ip)s %(color)s[%(asctime)s %(filename)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class HrFilter(logging.Filter):
    """
    为日志添加访问ip以及log_id
    """
    def filter(self, record):
        try:
            record.ip = RequestHandler.remote_ip
            record.log_id = RequestHandler.log_id
        except Exception as e:
            print(e)
            record.ip = 'no ip'
            record.log_id = 'no log_id'
        return True


# 文件日志
fileHandler = cloghandler.ConcurrentRotatingFileHandler(os.environ.get("hr_log_path"), "a", 512 * 1024 * 1024, 5)
fileHandler.setFormatter(LogFormatter())
# 控制台日志
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(LogFormatter())

# 初始化日志
code_logger = logging.getLogger('hr_code_log')
code_logger.setLevel(logging.INFO)
# 禁用上级传递，日志只不输出到上一级
code_logger.__setattr__('propagate', False)
# 增加handler
code_logger.addHandler(fileHandler)
code_logger.addHandler(streamHandler)
# 增加filter
code_logger.addFilter(HrFilter())

if __name__ == '__main__':
    code_logger.warning(2222)
    code_logger.error(2222)
    code_logger.info(2222)
