# encoding=utf-8

from restsql.check import check
from restsql.query import Query
from restsql.config.database import db_settings, EnumDataBase
from restsql.datasource.client import EsClient, PgClient, DruidClient

__all__ = ['RestClient']


class RestClient:
    """
    restsql主要服务类，服务器端调用，输入请求协议，输出DataFrame

    内部实现：
    根据请求协议识别查询的数据源，通过调用相应数据源的Client服务类，输出DataFrame
    """

    def __init__(self, query_dict):
        self.query_instance = Query(query_dict)

    # 供服务器端调用的接口
    def query(self):
        """
        restsql查询方法入口，启动该方法，对协议进行转义，查询，并返回结果

        :return: 数据对象
        """
        # 进行格式检查
        if self.query_instance.target is None:
            raise RuntimeError("The query target is empty")
        db_name = self.query_instance.target.split(".")[0]
        # 获取DataBase对象
        database = db_settings.get_by_name(db_name)
        if database is None:
            raise RuntimeError("no find the target table")
        check(self.query_instance, database)
        if database.db_type == EnumDataBase.ES:
            client = EsClient(database)
        elif database.db_type == EnumDataBase.PG:
            client = PgClient(database)
        else:
            client = DruidClient(database)
        return client.query(self.query_instance)
