import sys
import os
import time
import threading
from queue import Queue

# 获取项目根目录的绝对路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python路径中
sys.path.append(project_root)
os.environ['PYTHONPATH'] = 'C:\\Users\\31789\\Desktop\\sjc\\aics\\move'

from utils.chat import chat


