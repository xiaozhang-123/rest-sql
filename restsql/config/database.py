from elasticsearch import Elasticsearch
from pydruid.db import connect
from restsql.config.logger import rest_logger
import os
import sys
import psycopg2

__all__ = ['EnumDataBase', 'DataBase', 'db_settings']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


class EnumDataBase:
    """
    数据源类型枚举类
    """
    PG = 'PG'
    ES = 'ES'
    DRUID = 'DRUID'


class DataBase:
    """
    db_setting类。以对象的形式存储各个数据源的配置信息。
    """

    def __init__(self, name, db_type, host, db_name=None, port=None, user=None, password=None, schema=None,
                 tables=None, black_tables=None, black_fields=None):
        """
        db_setting初始化器。

        :param name: 该配置数据源的名称
        :param db_type: 数据库类型。由EnumDataBase枚举类定义。
        :param host: 数据库host。
        :param db_name: 数据库名。
        :param port: 端口名。
        :param user: 用户名。用于连接数据库。
        :param password: 密码。用户连接数据库。
        :param schema: 模式。用于pgsql数据源。
        :param tables: 表。作为list对象。
        :param black_tables: 黑名单表。是string的list。
        :param black_fields: 黑名单字段。
        """
        if tables is None:
            tables = []
        if black_fields is None:
            black_fields = {}
        if black_tables is None:
            black_tables = []
        self.name = name
        self.db_name = db_name
        self.db_type = db_type
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.schema = schema
        if isinstance(tables, list):
            self.tables = tables
        else:
            raise RuntimeError("List of class(extended from Table) needed.")
        if isinstance(black_tables, list):
            self.black_tables = black_tables
        else:
            raise RuntimeError("List of string(tables' name) needed.")
        if isinstance(black_fields, dict):
            self.black_fields = black_fields
        else:
            raise RuntimeError("Dict of table_name: [field_name] needed.")
        # 初始化连接Postgre
        if db_type == EnumDataBase.PG:
            if db_name is None or port is None or user is None or password is None:
                raise RuntimeError("Empty elements in PgSQL")
            self.conn = psycopg2.connect(database=db_name, user=user, password=password,
                                         host=host, port=port, keepalives=1)
        # 初始化连接Postgre
        elif db_type == EnumDataBase.DRUID:
            if host is None or port is None:
                raise RuntimeError("Empty elements in Druid")
            self.conn = connect(host=host, port=port)
        elif db_type == EnumDataBase.ES:
            if host is None or port is None:
                raise RuntimeError("Empty elements in Elasticsearch")
            self.conn = Elasticsearch(self.host + ":" + str(self.port))

    # 重新连接数据库
    def re_connect(self):
        rest_logger.logger.warning("数据库进行了重启")
        self.conn.close()
        if self.db_type == EnumDataBase.PG:
            self.conn = psycopg2.connect(database=self.db_name, user=self.user, password=self.password,
                                         host=self.host, port=self.port, keepalives=1)
        elif self.db_type == EnumDataBase.DRUID:
            self.conn = connect(host=self.host, port=self.port)

    # 获取数据库的连接对象（留以在取出连接对象时，确认其处于活动状态）
    def get_conn(self):
        if self.conn.closed:
            self.re_connect()
        return self.conn


class _DbSettings:

    def __init__(self):
        self._db_settings = {}

    def get_all_name(self):
        """
        获取当前db_settings中所有db_setting的name的list

        :return: List of db_settings' name
        """
        return self._db_settings.keys()

    def put(self, *db_setting_tuple):
        """
        向db_settings中直接添加db_setting实例

        :param db_setting_tuple: db_setting的可变参数列表
        :return: None
        """
        for db_setting in db_setting_tuple:
            if not isinstance(db_setting, DataBase):
                raise RuntimeError("DbSetting needed!")
            self._db_settings[db_setting.name] = db_setting

    def add(self, name, db_type, host, db_name=None, port=None, user=None, password=None, schema=None,
            tables=None, black_tables=None, black_fields=None):
        """
        向db_settings中添加新的db_setting类。

        :param name: 该db_setting的name。用于区分db_setting.
        :param db_type: 数据库类型。由EnumDataBase枚举类定义。
        :param host: 数据库host。
        :param db_name: 数据库名。
        :param port: 端口名。
        :param user: 用户名。用于连接数据库。
        :param password: 密码。用户连接数据库。
        :param schema: 模式。用于pgsql数据源。
        :param tables: 表。用户自定义相关表。是继承自Table类的类的list。
        :param black_tables: 黑名单表。是string的list。
        :param black_fields: 黑名单字段。是字典，结构为{'表名': ['字段名', ], }
        :return: None
        """
        self._db_settings[name] = DataBase(name, db_type, host, db_name, port, user, password, schema, tables,
                                           black_tables, black_fields)

    def get_by_name(self, name):
        """
        :param name: 待获取db_setting的name
        :return: db_setting
        """
        if name in self._db_settings:
            return self._db_settings[name]


#  以单例的方式生成db_settings
db_settings = _DbSettings()
