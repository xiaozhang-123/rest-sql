from restsql.config.logger import rest_logger

_all_ = ['EsQuery']


class EsQuery:
    """
    将请求协议转译为ES—DSL查询语句
    """

    def __init__(self, query):
        """
        :param query: 请求协议封装对象
        """
        self.limit = 1000
        if query.limit is not None:
            self.limit = query.limit
        self.index = query.target.split(".")[1]
        self.select_list = query.select_list
        self.time = query.time_dict
        self.group_list = query.group_list
        self.where_list = query.where_list
        self.dsl = {
            'size': 1000,  # default
            'query': {
                'bool': {
                    'must': []
                }
            },
            '_source': {
                'includes': []
            },
            'aggs': {
                'groupby': {
                    "composite": {
                        "sources": [

                        ]
                    },
                    'aggs': {}
                }
            },
        }
        self.dsl_where = self.dsl['query']['bool']['must']
        self.dsl_composite = self.dsl['aggs']['groupby']['composite']['sources']
        self.dsl_aggs = self.dsl['aggs']['groupby']['aggs']

    def _parse_fields(self):
        """
        return:DSL中增加将select部分的字段
        """
        for s in self.select_list:
            self.dsl['_source']['includes'].append(s["column"])

    def _parse_where(self):
        """
        过滤操作暂时仅支持了and

        :return:DSL中加入where筛选条件以及time字段的范围筛选
        """
        for filter_dic in self.where_list:
            if filter_dic["op"] == "=":
                self.dsl_where.append({
                    'term': {
                        filter_dic["column"]: filter_dic["value"]
                    }
                })
            elif filter_dic["op"] == "!=":
                self.dsl_where.append({
                    "bool": {
                        "must_not": [
                            {
                                "term": {
                                    filter_dic["column"]: filter_dic["value"]
                                }
                            }
                        ]
                    }})
            elif filter_dic["op"] == "<":
                self.dsl_where.append({
                    'range': {
                        filter_dic["column"]: {'lt': filter_dic["value"]}
                    }
                })
            elif filter_dic["op"] == ">":
                self.dsl_where.append({
                    'range': {
                        filter_dic["column"]: {'gt': filter_dic["value"]}
                    }
                })
            elif filter_dic["op"] == "<=":
                self.dsl_where.append({
                    'range': {
                        filter_dic["column"]: {'lte': filter_dic["value"]}
                    }
                })
            elif filter_dic["op"] == ">=":
                self.dsl_where.append({
                    'range': {
                        filter_dic["column"]: {'gte': filter_dic["value"]}
                    }
                })
            elif filter_dic["op"] == 'contains':
                self.dsl_where.append({
                    'wildcard': {filter_dic["column"]: ''.join(['*', filter_dic["value"], '*'])}
                })
            elif filter_dic["op"] == 'startswith':
                self.dsl_where.append({
                    'prefix': {filter_dic["column"]: filter_dic["value"]}
                })
            elif filter_dic["op"] == 'endswith':
                self.dsl_where.append({
                    'wildcard': {filter_dic["column"]: ''.join(['*', filter_dic["value"]])}
                })
            elif filter_dic["op"] == 'in':
                self.dsl_where.append({
                    'terms': {filter_dic["column"]: filter_dic["value"]}
                })
            elif filter_dic["op"] == 'not in':
                self.dsl_where.append({
                    "bool": {
                        "must_not": [
                            {
                                "terms": {
                                    filter_dic["column"]: filter_dic["value"]
                                }
                            }
                        ]
                    }})
            else:
                raise SyntaxError('cat not support op: {0}, field: {1}'.format(filter_dic["op"], filter_dic["column"]))
            # 将请求协议的yy:MM:dd hh:mm:ss格式转化为unix时间戳
        if self.time.get("column", "") != "" and self.time.get("begin", "") != "":
            self.dsl_where.append({
                'range': {
                    self.time["column"]: {'gte': self.time["begin"].replace(" ", "T", 1)}
                }
            })
        if self.time.get("column", "") != "" and self.time.get("end", "") != "":
            self.dsl_where.append({
                'range': {
                    self.time["column"]: {'lte': self.time["end"].replace(" ", "T", 1)}
                }
            })
        if len(self.dsl_where) == 0:
            del self.dsl["query"]

    def _parse_metric(self):
        """
        :return:  DSL中加入select中的聚合指标
        """
        func_map = {'count': 'value_count', 'sum': 'sum', 'avg': 'avg', 'max': 'max', 'min': 'min',
                    'count distinct': 'cardinality'}
        for s in self.select_list:
            if s.get("metric") in func_map.keys():
                alias = s.get("alias", "")
                if alias == "":
                    alias = s["column"]
                    if s.get("metric", "") != "":
                        alias = "{}({})".format(s["metric"], s["column"])
                self.dsl_aggs[alias] = {func_map[s["metric"]]: {'field': s["column"]}}
            else:
                if s.get("metric", "") == "":
                    continue
                raise SyntaxError('cat not support aggregation operation: {}'.format(s["metric"]))
        pass

    def _parse_composite(self):
        """
        :return: DSL加入分组以及时间聚合部分，若用户未指定Interval则默认为1s
        """
        for g in self.group_list:
            k = g.split(".")[0]
            sources_dict = {k: {"terms": {"field": g}}}
            self.dsl_composite.append(sources_dict)
        # 如果用户未填interval值，interval默认值为1s
        if len(self.time) != 0 and self.time.get("column", "") != "":
            if self.time.get("interval", "") == "":
                self.time["interval"] = "1s"
            sources_dict = {self.time["column"]: {"date_histogram": {"field": self.time["column"]}}}
            sources_dict[self.time["column"]]["date_histogram"]["interval"] = self.time["interval"]
            sources_dict[self.time["column"]]["date_histogram"]["format"] = "yyyy-MM-dd HH:mm:ss"
            sources_dict[self.time["column"]]["date_histogram"]["order"] = "asc"
            self.dsl_composite.append(sources_dict)
        if len(self.dsl_composite) == 0:
            del self.dsl["aggs"]
        else:
            self.dsl["size"] = 0
            self.dsl['aggs']['groupby']['composite']['size'] = self.limit

    def parse(self):
        """
        EsClient类调用的接口

        :return: 完整的DSL语句
        """
        self.dsl["size"] = self.limit
        self._parse_where()
        self._parse_composite()
        self._parse_fields()
        self._parse_metric()
        rest_logger.logger.info(self.dsl)
        return self.dsl
