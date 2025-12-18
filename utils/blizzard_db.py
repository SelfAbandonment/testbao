"""
暴雪账户数据库批量插入脚本
"""
import os
from datetime import datetime
from typing import Iterable, Tuple, List

import pymysql
from pymysql.err import OperationalError, IntegrityError
from log.log import *
from utils.config import get_mysql_config, get_account_file_path, get_separator

# MySQL连接配置
MYSQL_CONFIG = get_mysql_config()

# 账户文件与分隔符（可通过 .env 配置）
ACCOUNT_FILE_PATH = get_account_file_path()
DEFAULT_SEPARATOR = get_separator()

COMMON_SEPARATORS = [":", ",", " ", "\t"]

def split_line(line: str, preferred_sep: str) -> Tuple[str, str] | None:
    seps: List[str] = [preferred_sep] + [s for s in COMMON_SEPARATORS if s != preferred_sep]
    for sep in seps:
        parts = line.split(sep)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
    return None

def read_account_file(file_path: str, separator: str) -> list[tuple[str, str]]:
    account_list = []
    if not os.path.exists(file_path):
        logger.error(f"❌ 文本文件不存在：{file_path}")
        return account_list

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        pair = split_line(line, separator)
        if not pair:
            logger.warning(f"⚠️ 第{line_num}行格式错误，跳过：{line}")
            continue
        account_list.append(pair)
    logger.info(f"✅ 成功读取 {len(account_list)} 条有效账户密码")
    return account_list

def batch_insert_accounts(account_list: Iterable[tuple[str, str]]):
    account_list = list(account_list)
    if not account_list:
        logger.warning("⚠️ 无有效账户密码，跳过插入")
        return

    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        insert_sql = """
                     INSERT INTO blizzard_accounts (account, password)
                     VALUES (%s, %s)
                     ON DUPLICATE KEY UPDATE create_time = CURRENT_TIMESTAMP; \
                     """
        affected_rows = cursor.executemany(insert_sql, account_list)
        conn.commit()
        logger.info(f"✅ 批量插入完成，共处理 {len(account_list)} 条，成功插入/更新 {affected_rows} 条")

    except IntegrityError as e:
        logger.error(f"❌ 插入数据违反约束：{e}")
        if conn:
            conn.rollback()
    except OperationalError as e:
        logger.error(f"❌ 数据库连接/插入失败：{e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info(f"===== 插入暴雪账户开始（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）=====")
    account_list = read_account_file(ACCOUNT_FILE_PATH, DEFAULT_SEPARATOR)
    batch_insert_accounts(account_list)
    logger.info(f"===== 操作结束（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）=====")