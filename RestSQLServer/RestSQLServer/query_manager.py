# encoding=utf-8

class QueryManager:
    """
    权限管理模块，自定义用户查询控制
    """

    def __init__(self, request):
        """
        :param request: 权限检查需要的信息
        """
        self.body = request

    def query_check(self):
        """
        检查用户是否有访问权限
        :return:
        """
        return True

    def init(self):
        """
        访问初始化时执行
        :return:
        """
        pass

    def finally_query(self):
        """
        查询结束后处理
        :return:
        """
        pass
