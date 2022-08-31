# encoding=utf-8
import pandas as pd
from restsql.rest_client import *
from restsql.config.database import *

if __name__ == '__main__':
    query_dict = {
        "from": "es_test.test_index",
        "time": {
            "column": "time",
            "begin": "2001-07-20 02:34:23",
            "end": "2021-07-30",
            "interval": "1d"
        },
        "select": [
            {
                "column": "cityName.keyword",
                "alias": "cityName_count",
                "metric": "count"
            }
        ],
        "where": [
            {
                "column": "cityName",
                "op": "contains",
                "value": "a"
            }
        ],
        "group": ["address.keyword", "name.keyword"],
        "limit": 100
    }

    db_settings.add(
        name='es_test',
        db_type=EnumDataBase.ES,
        host='127.0.0.1',
        port=9200
    )
    client = RestClient(query_dict)
    result = client.query()
    print(result)
