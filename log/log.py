"""日志配置模块"""
import logging
import os
from datetime import datetime

log_dir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)