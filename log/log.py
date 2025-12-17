# log/log.py
import logging
import os
from datetime import datetime

# 日志目录不存在则创建
log_dir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 日志文件名（按日期）
log_file = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 日志级别：DEBUG/INFO/WARNING/ERROR
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),  # 写入文件
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 导出logger实例，供其他模块使用
logger = logging.getLogger(__name__)