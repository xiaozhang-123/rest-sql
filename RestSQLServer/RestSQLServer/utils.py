import datetime

__all__ = ['ResponseModel', 'frame_parse_obj', 'gen_restsql_query']

# 转dataframe为html格式
import json

from .config.load import table_map

"""
接口返回部分功能处理模块 
"""


def frame_parse_obj(df, key='json'):
    """
    查询数据返回格式转换

    :param df: 传入的返回dateframe
    :param key: 指定返回的格式
    :return: 返回转化后的格式
    """
    if key == 'html':
        return df.to_html()
    elif key == 'latex':
        return df.to_latex()
    elif key == 'txt':
        return df.to_string()
    return df.to_json(orient="columns", force_ascii=False)  # 默认是json，其他的形式不转化


def gen_restsql_query(target):
    """
    根据variable查询的输入语句，生成restql查询

    :param target: 查询variable接口请求target中的内容
    :return: restsql请求协议
    """
    return {
        "from": table_map[target["from"]],
        "select": [
            {
                "column": target["select"],
                "alias": "",
                "metric": ""
            }
        ],
        "where": [],
        "group": [],
        "limit": 1000
    }


class ResponseModel:
    """
    http response模板类

    success: {'status': 'ok','data':object,'time': current time}

    faulire: {'status': 'error','msg': error descripe}
    """

    def __init__(self, status):
        self._result = {
            'status': status,
            'time': datetime.datetime.now().strftime("  %Y-%m-%d %I:%M:%S %p ")
        }

    @staticmethod
    def success(data):
        """
        成功返回的模板生成方法

        :param data: 返回数据对象
        :return: 成功返回的json对象
        """
        resp = ResponseModel('200')
        resp._result['data'] = data
        return json.dumps(resp._result)

    @staticmethod
    def failure(status, msg):
        """
        失败返回的模板生成方法

        :param status: 错误状态
        :param msg: 错误信息
        :return: 错误返回的json结构
        """
        resp = ResponseModel(status)
        resp._result['msg'] = msg
        return json.dumps(resp._result)
