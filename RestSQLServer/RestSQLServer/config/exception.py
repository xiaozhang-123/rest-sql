__all__ = ['RestSqlExceptionBase', 'RunningException', 'UserConfigException',
           'ProgramConfigException']


class RestSqlExceptionBase(Exception):
    """
    RestSQL库所有异常的基类。
    code 0
    """

    def __init__(self, message, *args):
        self.message = message.format(args)


class RunningException(RestSqlExceptionBase):
    """
    运行时异常；查看日志并处理。
    code [1, 100]
    """

    def __init__(self, code, message, *args):
        self.message = message.format(args)


class UserConfigException(RestSqlExceptionBase):
    """
    用户相关异常；提示用户。
    code [101, 200]
    """
    pass


class ProgramConfigException(RestSqlExceptionBase):
    """
    检查异常；检查程序。
    code [301, 400]
    """
    pass
