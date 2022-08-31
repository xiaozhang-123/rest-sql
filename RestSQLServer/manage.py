#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


sys.path.extend([r'E:\f1ed-restsql-librestsql-master'])  # 这一句引入不要去掉，才能获取到restsql位置，后续处理，使用环境变量传入
from RestSQLServer.config.load import init_yaml, init_logger, CONF_RESTSQL_PATH, CONF_LOGGER_PATH


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RestSQLServer.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    init_yaml(CONF_RESTSQL_PATH)
    init_logger(CONF_LOGGER_PATH)
    main()
