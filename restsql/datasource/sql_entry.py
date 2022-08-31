# encoding=utf-8

from restsql.config.database import EnumDataBase
from restsql.config.logger import rest_logger
from restsql.query import Query


def _pg_bucket(interval=None):
    """
    将RestSql格式的时间间隔转换成秒数返回给pg聚合使用

    :param interval: RestSql格式的时间间隔
    :return: 秒数
    """
    # 默认时间间隔为1s
    if interval is None:
        return 1
    # 时间单位所对应的秒数
    time_bucket = {"y": 31557600, "M": 2629800, "w": 604800, "d": 86400,
                   "h": 3600, "m": 60, "s": 1}
    # 转换成秒数返回
    return time_bucket[interval[-1]] * int(interval[:-1])


def _druid_bucket(interval=None):
    """
    将RestSql格式的时间间隔转换成Druid支持的格式

    :param interval: RestSql格式的时间间隔
    :return: Druid支持的时间间隔格式
    """
    if interval is None:
        return 'PT1S'
    # RestSql单位对应的Druid时间间隔格式，?当作占位符，后面用来替换为数字
    time_bucket = {"y": "P?Y", "M": "P?M", "w": "P?W", "d": "P?D",
                   "h": "PT?H", "m": "PT?M", "s": "PT?S"}
    return time_bucket[interval[-1]].replace('?', interval[:-1])


def _build_bucket(sql_type, interval='1s'):
    """
    将RestSql格式的时间间隔转换成对应Sql类型的时间间隔

    比如1h转换成Druid中的PT1H，PG中的3600（PG全转换成秒数）

    :param interval: RestSql格式的时间间隔
    :param sql_type: 数据源类型
    :return: 对应Sql类型的时间间隔
    """
    if sql_type == EnumDataBase.PG:
        return "'{}'".format(_pg_bucket(interval))
    elif sql_type == EnumDataBase.DRUID:
        return "'{}'".format(_druid_bucket(interval))


def _build_select(select, time, sql_type):
    """
    完成SELECT这一部分的SQL代码转化

    :param select: 所需查询的所有字段的字典
    :param time: 包含时序处理信息的字典
    :return: SELECT这一部分的SQL代码
    """
    # 将每次得到的部分sql语句放在一个列表中，最后调用join连接在一起，避免浪费内存
    sql_list = []
    # 判断时间这一字段是否设置
    if time and 'column' in time and len(time['column']) > 0:
        time_select_sql = ''  # 时间这一字段的SELECT的SQL语句
        # 判断属于什么类型的SQL（比如Druid和Postgre在时间处理上有些许不同）
        if sql_type == EnumDataBase.DRUID:
            time_select_sql = 'SELECT TIME_FLOOR("{column}", {bucket}) AS "time"' \
                .format(column=time['column'], bucket=_build_bucket(EnumDataBase.DRUID,
                                                                    time['interval'] if 'interval' in time else None))
        elif sql_type == EnumDataBase.PG:
            time_select_sql = 'SELECT to_timestamp(floor(extract(epoch from "{column}")/{bucket})*{bucket}) AS "time" ' \
                .format(column=time['column'], bucket=_build_bucket(EnumDataBase.PG,
                                                                    time['interval'] if 'interval' in time else None))
        sql_list.append(time_select_sql)
        # 当存在时序字段，且还有其他需要查询的字段，添加逗号
        if len(select) > 0:
            sql_list.append(',')
    # 当既不存在时序字段也没有任何需要查询的字段时报错
    elif len(select) == 0:
        raise RuntimeError('SELECT is empty!')
    # 无时序字段，有其他需要查询的字段（即普通的表查询）
    elif len(select) > 0:
        sql_list.append('SELECT ')
    # 遍历生成所有字段的SQL代码
    for s in select:
        if 'column' not in s:
            RuntimeError('The column cannot be empty')
        # 判断是否使用聚合函数
        if 'metric' in s and len(s['metric']) > 0:
            # count distinct使用格式较为特殊，单独处理
            if s['metric'] in ['COUNT DISTINCT', 'count distinct']:
                sql_list.append('COUNT(DISTINCT "{column}") '.format(column=s['column']))
            else:
                sql_list.append('{metric}("{column}") '.format(metric=s['metric'], column=s['column']))
        else:
            sql_list.append('"{column}" '.format(column=s['column']))
        # 判断是否有别名
        if 'alias' in s and len(s['alias']) > 0:
            sql_list.append(
                'AS {alias} '.format(alias=s['alias'])
            )
        sql_list.append(',')
    return ''.join(sql_list)[:-1]  # 连接select这部分的完整sql，且去掉末尾多的一个逗号后返回


def _build_filter(filters, time, param_dic):
    """
    完成WHERE这一部分的SQL代码转化（带占位符）， 以及完整对参数列表的处理

    例如 生成的SQL为 WHERE price > %(price)s AND type = %(type)s，参数列表param_dic为{'price':'100', 'type':'book'}

    :param filters: 所需过滤条件的列表
    :param time: 包含时序处理信息的字典
    :param param_dic: where中value构成的列表
    :return: WHERE这一部分带占位符的SQL代码
    """
    # 若没有任何过滤条件（包括时间）
    if (not time or 'column' not in time or len(time['column']) == 0) and len(filters) == 0:
        return ''
    # 将每次得到的部分sql语句放在一个列表种，最后调用join连接在一起，避免浪费内存
    filter_list = []
    # 若存在时序字段，则将此添加到第一个filter（当无时序字段的时候，相当于普通的表查询）
    if time and 'column' in time and len(time['column']) > 0:
        if 'begin' in time and len(time['begin']) > 0:
            filter_list.append("\"{time}\">='{begin}' ".format(time=time['column'], begin=time['begin']))
        if 'end' in time and len(time['end']) > 0:
            filter_list.append("\"{time}\"<='{end}' ".format(time=time['column'], end=time['end']))
    for f in filters:
        filter_list.append(_filter_handler(f, param_dic))
    return 'WHERE {filter}'.format(filter=' AND '.join(filter_list))


def _filter_handler(filter_dic, param_dic):
    """
    处理单个filter，将收到的字典里的信息提取出来，生成一个带占位符的表达式，并处理完value后添加到param_dic中

    druid的python驱动不支持使用例如 WHERE a > %s AND b > %s,['1', '2']这种格式化传参，而是使用字典方式格式化

    例如 '%(a)s, %(b)s' % {'a':'xx', 'b':'xx'},为了统一Druid和Postgre，这里均使用了字典，而每个的键为这个值插入的序号，

    例如 '%(0)s, %(1)s' % {'0':'xx', '1':'xx'},序号的生成方式为str(len(param_dic) - 1)

    :param filter_dic: 包含一个filter信息的字典
    :param param_dic: where中value构成的字典
    :return: 带占位符的表达式, 例如：price > %(p1)s
    """
    # 特殊的比较符
    filter_op = {"startswith": "?%", "endswith": "%?", "contains": "%?%"}
    # 对普通比较符的处理
    if filter_dic['op'] not in filter_op.keys():
        # 直接将value的值加入到param_list中
        param_dic[str(len(param_dic))] = filter_dic['value']
        return '"{column}" {op} %({index})s '.format(column=filter_dic['column'], op=filter_dic['op'],
                                                     index=str(len(param_dic) - 1))
    # 对filter_op里的操作符的处理
    # 将value更改为filter_op中对应比较符所需要的格式再添加到param_dic里
    param_dic[str(len(param_dic))] = filter_op[filter_dic['op']].replace('?', filter_dic['value'])
    return '"{column}" like %({index})s '.format(column=filter_dic['column'], index=str(len(param_dic) - 1))


def _build_group(group_list, time, sql_type):
    """
    完成GROUP这一部分SQL代码转化

    :param group_list: 需要分组的字段名列表
    :param time: 包含时序处理信息的字典
    :param sql_type: 需要生成的Sql类型，比如Druid或Postgresql
    :return: GROUP这一部分的SQL代码
    """
    # 若既没时序字段也没任何需要分组的字段，直接返回空字符串
    if (not time or 'column' not in time or len(time['column']) == 0) and len(group_list) == 0:
        return ''
    res_list = []
    # 判断sql类型（在group处理上pg和druid有不同，druid需要加单引号，pg为了区分大小写，同一加双引号）
    if sql_type == EnumDataBase.DRUID:
        # 若存在时序字段，则将时序字段放在第一个GROUP
        if time and 'column' in time and len(time['column']) > 0:
            res_list.append('1')
        res_list.extend(["{}".format(i) for i in group_list])
    elif sql_type == EnumDataBase.PG:
        # 若存在时序字段，则将时序字段放在第一个GROUP
        if time and 'column' in time and len(time['column']) > 0:
            res_list.append('"time"')
        res_list.extend(['"{}"'.format(i) for i in group_list])
    return 'GROUP BY {} '.format(','.join(res_list))


def to_sql(que: Query, sql_type, schema=None):
    """
    把需要查询的内容转化为普通的SQL语句

    :param schema: schema对象,例如postgre里的public
    :param sql_type: 需要生成的Sql类型，比如Druid或Postgresql
    :param que: 包含查询所需信息的Query对象
    :return: 带占位符的普通SQL语句和where部分的参数字典构成的元组，
             例如('SELECT name, price FROM sale WHERE price >= %(price)s', ['price':'100'])
    """
    # where中的value构成的字典
    param_dic = {}
    if schema is None:
        source = 'FROM "{}" '.format(que.target.split('.')[1])  # 数据源
    else:
        source = 'FROM "{}"."{}" '.format(schema, que.target.split('.')[1])  # 为postgresql添加schema
    select = _build_select(que.select_list, que.time_dict, sql_type)  # 字段这部分sql
    filters = _build_filter(que.where_list, que.time_dict, param_dic)  # 过滤条件
    group = _build_group(que.group_list, que.time_dict, sql_type)  # 分组
    limit = 'LIMIT ' + str(que.limit)  # 数据量
    # 若存在时间字段则按第一个字段排序（即时序）， 否则默认排序
    sort = 'ORDER BY 1 ' if que.time_dict and 'column' in que.time_dict and len(que.time_dict['column']) > 0 else ''
    sql = select + source + filters + group + sort + limit  # 最终的sql拼接
    rest_logger.logger.info("sql: {}  paramdict: {}".format(sql, param_dic))
    return sql, param_dic


def get_columns(que: Query):
    """
    获取需要查询的所有字段名

    :param que: 包含查询信息的Query封装对象
    :return: 所有字段名构成的列表
    """
    columns = []  # 默认把时间添加到第一个列
    if que.time_dict and 'column' in que.time_dict and len(que.time_dict['column']) > 0:
        columns.append('time')
    # 获取返回结果的名字（字段名或别名）
    for i in que.select_list:
        c = i['column']
        if 'alias' in i and len(i['alias']) > 0:
            c = i['alias']
        columns.append(c)
    return columns
