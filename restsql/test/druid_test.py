# encoding=utf-8

import json
from restsql.config.database import DataBase, EnumDataBase
from restsql.datasource.client import DruidClient
from restsql.query import Query


data_json = '''
{
    "from":"test.wikipedia",
    "time":{
      "column":"__time",
      "begin":"2015-7-20",
      "end":"2017-7-30",
      "interval":"1s"
    },
    "select":[
      {
        "column":"commentLength",
        "alias":"评论平均字数",
        "metric":"avg"
      },
      {
        "column":"commentLength",
        "alias":"评论总字数",
        "metric":"SUM"
      }
    ],
    "where":[],
    "group":[],
     "limit":10000
  }
'''

database = DataBase(name='test', db_type=EnumDataBase.DRUID, port='8888', host='localhost')
client = DruidClient(database)
que = Query(json.loads(data_json))
print(client.query(que))
