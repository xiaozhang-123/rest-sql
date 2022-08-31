# encoding=utf-8

import json
from restsql.config.database import DataBase, EnumDataBase
from restsql.datasource.client import PgClient
from restsql.query import Query


data_json = '''
{
    "from":"test.sale",
    "time":{
      "column":"",
      "begin":"2021-7-20",
      "end":"2021-7-30",
      "interval":"1d"
    },
    "select":[
      {
        "column":"name",
        "alias":"",
        "metric":""
      },
      {
        "column":"price",
        "alias":"平均价格",
        "metric":"avg"
      }
    ],
    "where":[
      {
       "column":"price",
       "op": "<=",
       "value": "200"
      }
    ],
    "group":["name"],
     "limit":1000
  }
'''

database = DataBase(name='test', db_type=EnumDataBase.PG, port='5432', db_name='test',
                    host='localhost', user='postgres', password='12345')
query = Query(json.loads(data_json))
client = PgClient(database)
print(client.query(query))
