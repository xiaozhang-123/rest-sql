import os
import sys

# 此处手动把路径添加到环境变量，否则出现module no find
ServerConfigPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(ServerConfigPath)
