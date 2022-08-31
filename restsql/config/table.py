# -*- coding:utf-8 -*-


class Field(object):
    """
    表字段类型定义基类
    """
    pass


class IntField(Field):
    """
    整数类型: IntegerField
    """
    pass


class NumberField(Field):
    """
    数字类型: DoubleField
    """
    pass


class StringField(Field):
    """
    字符串类型: TextField
    """
    pass


class BoolField(Field):
    """
    布尔类型: BooleanField
    """
    pass


class TimeField(Field):
    """
    时间类型 DateTimeField
    """
    pass


class Table(object):
    """
    Schema基类
    """
    pass
