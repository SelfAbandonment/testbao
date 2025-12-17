# utils/read_account.py
import json
from pathlib import Path
from typing import Dict, List

from log.log import logger
from .mysqlDao import get_accounts


def read_account(limit: int = 1, source: str = "db", fallback_file: str = "accounts.json") -> Dict:
    """返回单个账号信息，优先数据库，可降级到本地文件."""
    accounts = read_accounts(limit=limit, source=source, fallback_file=fallback_file)
    return accounts[0] if accounts else {}


def read_accounts(limit: int = 10, source: str = "db", fallback_file: str = "accounts.json") -> List[Dict]:
    if source == "db":
        try:
            accounts = get_accounts(limit)
            if accounts:
                return accounts
        except Exception:
            logger.warning("数据库读取账号失败，回退到本地文件")
    return read_from_file(fallback_file)


def read_from_file(file_path: str) -> List[Dict]:
    path = Path(file_path)
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def get_account_list(limit: int = 10):
    return read_accounts(limit=limit)
