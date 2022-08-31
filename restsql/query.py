# encoding=utf-8

__all__ = ['Query']
"""
请求协议的封装类
"""


class Query:
    """
    数据库查询基类
    """
    def __init__(self, query_dict):
        """
        数据库查询服务基类

        :param query_dict: 将请求协议字典封装为类，并将协议缺失部分置空
        """
        self.target = query_dict.get("from", "")
        self.time_dict = query_dict.get("time", {})
        self.select_list = query_dict.get("select", [])
        self.where_list = query_dict.get("where", [])
        self.group_list = query_dict.get("group", [])
        self.limit = query_dict.get("limit", 1000)
