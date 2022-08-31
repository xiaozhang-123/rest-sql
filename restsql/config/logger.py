import os
import logging
import sys
import time

__all__ = ["Logger", "rest_logger"]


class Logger:
    """
    日志模块处理配置类

    logfile:指定日志输出文件名，默认以生成该日志类单例对象的绝对路径下面生成日志文件（如果没有指定文件名，那么将默认生成一个)
    日志输出相关参数

    levelname: 日志级别名

    asctime: 易读时间格式

    name: 当前调用logger记录器名称（当前运行该logger语句是在哪一个文件)

    lineno: 调用输出日志的源码所在行数

    filename: 输出日志的文件名

    threadName: 线程名

    process: pid值

    message: 日志输出信息
    """

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)  # 首先整个日志指定最低日志严重级别
        self.formater = logging.Formatter('restsql:  %(levelname)s  %(asctime)s  %(name)s  %(filename)s  %(lineno)d  '
                                          '%(threadName)s  pid:%(process)d  %(message)s')

        self.stream_handler = logging.StreamHandler(sys.stdout)  # 终端输出日志处理器
        self.stream_handler.setFormatter(self.formater)
        self.stream_handler.setLevel(logging.WARNING)  # 可以额外设置优先级
        self.logger.addHandler(self.stream_handler)

    def set_level(self, level="WARNING"):
        """"
        设置该logger对象的日志记录级别,默认WARNING（低于该级别的不在终端输出)
        """
        if level == "ERROR":
            self.logger.setLevel(logging.ERROR)
        elif level == "DEBUG":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

    def set_file_logger(self, logfile=None):  # 设置文件日志管理器
        """
        设置文件日志

        :param logfile: 文件路径
        :return: None
        """
        if logfile is None:
            cur_path = os.path.split(os.path.realpath(__file__))[0]
            stime = time.strftime("%Y-%m-%d", time.localtime())
            logfile = cur_path + os.sep + "log_" + stime + ".log"  # os.sep 通用文件路径分隔符
        else:
            logfile = logfile  # 这里如果有指定路径，设置变量

        self.file_handler = logging.FileHandler(logfile)  # 文件日志处理器
        self.file_handler.setFormatter(self.formater)
        self.logger.addHandler(self.file_handler)

        self.logger.debug("logfile path: {}".format(logfile))


rest_logger = Logger()  # 作为单例对象，（在对象被生成后进行调用
