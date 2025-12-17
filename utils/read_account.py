# utils/read_account.py
from .mysqlDao import get_accounts  # 从数据库读取
# 或从文件读取（示例）
import json

def read_from_file(file_path="accounts.json"):
    """从JSON文件读取账号列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_account_list(limit=10):
    """对外提供账号列表（优先从数据库读取，可切换为文件）"""
    return get_accounts(limit)
    # return read_from_file()