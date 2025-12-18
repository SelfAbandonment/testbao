"""
暴雪账户数据库批量插入脚本
"""
from log.log import *
import pymysql
from pymysql.err import OperationalError, IntegrityError
import os
from datetime import datetime

# MySQL连接配置
MYSQL_CONFIG = {
    "host": "localhost",       # 数据库地址（本地填localhost）
    "port": 3306,              # 端口（默认3306）
    "user": "root",            # 数据库用户名
    "password": "ypXZQGkKg0mp4gdQ",  # 数据库密码（替换为你的密码）
    "db": "blizzard_db",       # 要创建/使用的数据库名
    "charset": "utf8mb4"       # 字符集（避免中文乱码）
}

# 账户密码文本文件路径
ACCOUNT_FILE_PATH = "D:\\code\\gametest\\blizzard_accounts.txt"

# 文本文件中账户和密码的分隔符（支持: / 空格 / ,，根据你的文件修改）
SEPARATOR = ":"

def read_account_file(file_path, separator):
    """
    读取文本文件中的账户密码，返回格式化的列表
    :param file_path: 文本文件路径
    :param separator: 账户和密码的分隔符
    :return: 列表，每个元素是元组 (account, password)
    """
    account_list = []
    if not os.path.exists(file_path):
        logger.error(f"❌ 文本文件不存在：{file_path}")
        return account_list

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        # 去除行首尾空格/换行符
        line = line.strip()
        if not line:
            continue
        # 分割账户和密码
        parts = line.split(separator)
        if len(parts) != 2:
            logger.warning(f"⚠️ 第{line_num}行格式错误（非 账户{separator}密码 格式），跳过：{line}")
            continue
        account = parts[0].strip()
        password = parts[1].strip()
        account_list.append((account, password))
    logger.info(f"✅ 成功读取 {len(account_list)} 条有效账户密码")
    return account_list

def batch_insert_accounts(account_list):
    """
    批量插入账户密码到MySQL数据库
    :param account_list: 格式为 [(account1, password1), (account2, password2), ...]
    """
    if not account_list:
        logger.warning("⚠️ 无有效账户密码，跳过插入")
        return

    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        # 批量插入SQL（ON DUPLICATE KEY UPDATE 避免重复插入时报错，仅更新时间）
        insert_sql = """
                     INSERT INTO blizzard_accounts (account, password)
                     VALUES (%s, %s)
                         ON DUPLICATE KEY UPDATE create_time = CURRENT_TIMESTAMP; \
                     """
        # 执行批量插入（executemany效率远高于单条插入）
        affected_rows = cursor.executemany(insert_sql, account_list)
        conn.commit()
        logger.info(f"✅ 批量插入完成，共处理 {len(account_list)} 条，成功插入/更新 {affected_rows} 条")

    except IntegrityError as e:
        logger.error(f"❌ 插入数据违反约束（如唯一索引）：{e}")
        conn.rollback()
    except OperationalError as e:
        logger.error(f"❌ 数据库连接/插入失败：{e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info(f"===== 插入暴雪账户开始（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）=====")
    account_list = read_account_file(ACCOUNT_FILE_PATH, SEPARATOR)
    batch_insert_accounts(account_list)
    logger.info(f"===== 操作结束（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）=====")