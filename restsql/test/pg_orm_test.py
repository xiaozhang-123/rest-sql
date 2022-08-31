# import peewee
#
# from restsql.config.model import Client, Query
# from restsql.config.table import Table
# from peewee import Model, fn, TextField, IntegerField, DoubleField, BooleanField, DateTimeField
# import pandas as pd
# from restsql.config.table import StringField, IntField, BoolField, NumberField, TimeField
#
# __all__ = ['PgClient']
#
#
# def parse_fields_peewee(fields):
#     new_fields = {}
#     for field, field_type in fields.items():
#         if isinstance(field_type, StringField):
#             new_fields[field] = TextField()
#         elif isinstance(field_type, IntField):
#             new_fields[field] = IntegerField()
#         elif isinstance(field_type, NumberField):
#             new_fields[field] = DoubleField()
#         elif isinstance(field_type, BoolField):
#             new_fields[field] = BooleanField()
#         elif isinstance(field_type, TimeField):
#             new_fields[field] = DateTimeField()
#     return new_fields
#
#
# class PGQuery:
#     def __init__(self, query, database):
#         self.query = query
#         self.database = database
#         self.table = self._get_table()
#
#     def get_model(self):  # 动态类型模板类
#         if not self.table:
#             raise RuntimeError("not find the target table")
#         if self.table.__bases__[0] != Table:
#             raise RuntimeError("the table base class error")
#
#         class ModelBase(Model):
#             class Meta:
#                 database = self.database.db
#                 schema = getattr(self.database, 'schema', None)
#
#         new_fields = parse_fields_peewee(self.table.fields)
#         table_model = type(str(self.table.table_name), (ModelBase,), new_fields)  # 动态类型
#         self.model = table_model  # 生成动态表 peewee操作model
#
#     def _get_table(self):
#         table_name = self.query.From.split(".", 1)[-1]
#         for table in self.database.tables:
#             if table.table_name == table_name:
#                 return table
#         return None
#
#     def pgsql_query(self):
#         self.get_model()  # 生成模型
#         time_dict = self.query.time_dict
#         time_flag = False  # 判断后续是否要pandas进行处理
#         where_params = self.extract_where_params()
#         group_params = self.extract_group_params()
#         if time_dict.get('column', None):
#             if time_dict.get('begin', None):
#                 where_params.append(getattr(self.model, time_dict['column']) > time_dict['begin'])
#             if time_dict.get('end', None):
#                 where_params.append(getattr(self.model, time_dict['column']) < time_dict['end'])
#             if time_dict.get('interval', None):  # 这里进行时间处理，不事先进行聚合
#                 select_params, select_metric = self.extract_no_metric_select_params()
#                 select_params.append(getattr(self.model, time_dict['column']))
#                 time_flag = True
#             else:
#                 select_params = self.extract_select_params()
#         else:
#             select_params = self.extract_select_params()
#             print("hhh")
#             print(len(select_params))
#         self.results = self.model.select(*select_params)  # 变为可变形参传进去
#         if len(where_params) > 0:
#             self.results = self.results.where(*where_params)
#
#         if len(group_params) > 0:
#             self.results = self.results.group_by(*group_params)
#         limit_size = self.query.limit
#         if limit_size:
#             self.results = self.results.limit(limit_size)
#         if time_flag:
#             return self.handle_time_bucket(select_metric)
#         print(self.results)
#         return pd.DataFrame(self.results.dicts())
#
#     def extract_group_params(self):
#         try:
#             group_params = [getattr(self.model, field) for field in self.query.group_list]
#         except Exception as e:
#             raise RuntimeError("the group param is false")
#
#         return group_params
#
#     def extract_where_params(self):  # 仅仅或处理
#         wheres = self.query.where_list
#         where_params = []  # model.where() 的where里面默认传入不定长参数
#         for i in range(0, len(wheres)):
#             temp = wheres[i]
#             if temp.get('column', None) and temp.get('op', None) and temp.get('value', None):
#                 if temp['op'] == '=':
#                     where_params.append(getattr(self.model, temp['column']) == temp['value'])
#                 elif temp['op'] == '>':
#                     where_params.append(getattr(self.model, temp['column']) > temp['value'])
#                 elif temp['op'] == '>=':
#                     where_params.append(getattr(self.model, temp['column']) >= temp['value'])
#                 elif temp['op'] == '<':
#                     where_params.append(getattr(self.model, temp['column']) < temp['value'])
#                 elif temp['op'] == '<=':
#                     where_params.append(getattr(self.model, temp['column']) <= temp['value'])
#                 elif temp['op'] == '!=':
#                     where_params.append(getattr(self.model, temp['column']) != temp['value'])
#                 elif temp['op'] == 'startswith':
#                     where_params.append(getattr(self.model, temp['column']).startswith(temp['value']))
#                 elif temp['op'] == 'endswith':
#                     where_params.append(getattr(self.model, temp['column']).endswith(temp['value']))
#                 elif temp['op'] == 'between':
#                     if isinstance(temp['value'], list) and len(temp['value']) == 2:
#                         where_params.append(getattr(self.model, temp['column']).between(temp['value']))
#                     else:
#                         raise RuntimeError("value must be list and the value list size must be 2")
#                 elif temp['op'] == 'in':
#                     if isinstance(temp['value'], list):
#                         where_params.append(getattr(self.model, temp['column']).in_(temp['value']))
#                     else:
#                         raise RuntimeError("the value must be list if operate is in")
#                 else:
#                     raise RuntimeError("the operate {} is no found", temp['op'])
#             else:
#                 raise RuntimeError("wrong format")
#         return where_params
#
#     def extract_select_params(self):
#         select_params = []
#         for select_item in self.query.select_list:
#             if len(select_item.get('column', "")) < 1:
#                 raise RuntimeError("the select column is empty")
#             if select_item.get("metric", None) is None:
#                 select_param = getattr(self.model, select_item['column']).alias(
#                     select_item.get('alias', ""))  # 如果metric 这一个字段没有出现，说明不指定聚合
#                 select_params.append(select_param)
#             elif select_item['metric'] in ['count', 'avg', 'max', 'min', 'count', 'sum']:
#                 select_param = getattr(fn, select_item['metric'])(getattr(self.model, select_item['column'])).alias(
#                     select_item.get('alias', ""))  # 类似于 sum(item)
#                 select_params.append(select_param)
#             elif select_item['metric'] == 'distinct':
#                 select_param = fn.Distinct(getattr(self.model, select_item['metric'])).alias(
#                     select_item.get('alias', ""))
#                 select_params.append(select_param)
#             else:
#                 raise RuntimeError("metric {} is invalid".format(select_item))
#         return select_params
#
#     def extract_no_metric_select_params(self):  # 使用pandas方案进行时间聚合，在此处数据库不事先使用聚合
#         select_dict = {'select_params': [],
#                        'select_metric': {}}  # 这里第一个是自做alias处理的，select param数组，另一个是每一个字段要聚合的方式，方便后期pandas处理
#         for select_item in self.query.select_list:
#             if len(select_item.get('column', "")) < 1:
#                 raise RuntimeError("the select column is empty")
#             column = getattr(self.model, select_item['column']).alias(select_item.get('alias', ""))
#             select_dict['select_params'].append(column)
#             if select_item.get('metric', None):
#                 if select_item['metric'] in ['count', 'avg', 'max', 'min', 'count', 'sum', 'distinct']:
#                     key = select_item.get('alias', False) if select_item['alias'] else select_item['column']
#                     select_dict['select_metric'][key] = select_item['metric']
#                     # 如果alias存在，那么最终Pandas就用这个判断，否则使用原名字
#                 else:
#                     raise RuntimeError("metric {} is invalid".format(select_item))
#         return select_dict['select_params'], select_dict['select_metric']
#
#     def handle_time_bucket(self, metric):
#         if len(metric.keys()) < 1:
#             raise RuntimeError("the metric can't be empty")
#         print(self.results)
#         df = pd.DataFrame(self.results.dicts())
#         time_column = self.query.time_dict['column']
#         df[time_column] = pd.to_datetime(df[time_column])  # 整理标准时间格式
#         return df.resample(self.query.time_dict['interval'], on=time_column).agg(metric) # 使用pandas 进行时间切片
#
#
# class PgClient(Client):
#     """
#     提供给外界的接口类
#     """
#
#     def __init__(self, database):
#         self.dataBase = database
#
#     def query(self, que: Query):
#         pg_query = PGQuery(que, self.dataBase)
#         try:
#             df = pg_query.pgsql_query()
#         except peewee.InternalError as e:
#             self.dataBase.db.rollback()
#         return df
