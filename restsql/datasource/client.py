# encoding=utf-8

from restsql.config.database import EnumDataBase
from restsql.datasource.sql_entry import to_sql, get_columns
from sqlalchemy.exc import CompileError
from pydruid.db.exceptions import Error
from restsql.datasource.es_entry import EsQuery
import psycopg2
import pandas as pd

__all__ = ['Client', 'DruidClient', 'PgClient', 'EsClient']

from restsql.query import Query


class Client:
    def __init__(self, database):
        """
        :param database: dataBase对象
        """
        self.database = database

    def query(self, que):
        """
        :param que: 请求协议的封装类Query对象
        :return: DataFrame格式数据
        """
        raise NotImplementedError
        pass


class DruidClient(Client):
    """
    Druid数据源
    """

    def query(self, que):
        sql, param_dic = to_sql(que, EnumDataBase.DRUID, self.database.schema)
        conn = self.database.get_conn()
        try:
            curs = conn.cursor()
            curs.execute(sql, param_dic)
        except CompileError as e:
            print(e)
            raise RuntimeError(str(e).split('\n')[0])
        except Error as e:
            raise RuntimeError(str(e).split(':')[-1])
        res = curs.fetchall()
        curs.close()
        columns = get_columns(que)
        return pd.DataFrame(data=res, columns=columns)


class PgClient(Client):
    """
    提供给外界的接口类
    """

    def query(self, que: Query):
        sql, param_dic = to_sql(que, EnumDataBase.PG, self.database.schema)
        conn = self.database.get_conn()
        columns = get_columns(que)
        # 调用数据库，得到sql语句查询的结果
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, param_dic)
                rows = cursor.fetchall()
        except psycopg2.Error as e:
            # 若查询过程中出现问题，则回滚
            conn.rollback()
            # 回滚后尝试一次简单查询，若出错则重新连接
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT 1')
            except psycopg2.Error:
                # 若查询过程中出现问题，则重新建立连接，并抛出错误
                self.database.re_connect()
            raise RuntimeError(str(e).split('\n')[0])
        # 以dataFrame格式返回
        return pd.DataFrame(data=rows, columns=columns)


class EsClient(Client):
    """
    Es数据源服务类，供restSqlClient调用
    """

    def query(self, que):
        # 保存别名的字典
        alias_dict = {}
        # 保存不进行聚合的字段和别名
        no_agg_field = []
        for s in que.select_list:
            alias_dict[s["column"]] = s.get("alias", s["column"])
            if s.get("metric", "") == "":
                if s.get("alias", "") == "":
                    s["alias"] = s["column"]
                no_agg_field.append([s["column"], s["alias"]])
        if que.time_dict.get("column", "") != "":
            alias_dict[que.time_dict["column"]] = "time"

        results = []
        index = que.target.split(".")[1]
        esQuery = EsQuery(que,)
        dsl = esQuery.parse()
        raw_result = self.database.conn.search(index=index, body=dsl)
        # 根据聚合与否,从两个地方进行遍历取值
        if 'aggs' in raw_result or 'aggregations' in raw_result:
            if raw_result.get('aggregations'):
                results = raw_result['aggregations']['groupby']['buckets']
            else:
                results = raw_result['agg']['groupby']['buckets']
            for it in results:
                for f in no_agg_field:
                    it[f[1]] = it["key"].get(f[0])
                it["time"] = it["key"].get(que.time_dict.get("column", None), None)
                if it["time"] is None:
                    del it["time"]
                del it['key']
                del it['doc_count']
                for field, value in it.items():
                    if isinstance(value, dict) and 'value' in value:
                        it[field] = value['value']
        elif 'hits' in raw_result and 'hits' in raw_result['hits']:
            for it in raw_result['hits']['hits']:
                record = it['_source']
                result = {}
                for field in record.keys():
                    if alias_dict[field] == "":
                        result[field] = record[field]
                    else:
                        result[alias_dict[field]] = record[field]
                results.append(result)
        return pd.DataFrame(results)
