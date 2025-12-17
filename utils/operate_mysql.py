# utils/operate_mysql.py
import os
from contextlib import contextmanager
from typing import Any, Dict, List

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor


def _load_db_config() -> Dict[str, Any]:
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'ypXZQGkKg0mp4gdQ'),
        'database': os.getenv('DB_NAME', 'battle_net'),
        'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
        'maxconnections': int(os.getenv('DB_MAX_CONNECTIONS', '10')),
        'cursorclass': DictCursor,
    }


pool = PooledDB(creator=pymysql, **_load_db_config())


def get_conn():
    return pool.connection()


@contextmanager
def get_cursor():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def execute_sql(sql: str, args=None):
    with get_cursor() as cursor:
        cursor.execute(sql, args)
        return cursor.rowcount


def selectOne(table_name: str) -> List[Dict]:
    sql = f"SELECT * FROM {table_name} WHERE last_check IS NULL OR last_check = 0 LIMIT 1"
    with get_cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def updateOneById(table_name: str, last_check, card: Dict):
    sql = f"UPDATE {table_name} SET last_check=%s WHERE id=%s"
    with get_cursor() as cursor:
        cursor.execute(sql, (last_check, card['id']))


def selectCount(table_name: str):
    sql = f"SELECT COUNT(*) as count FROM {table_name} WHERE last_check IS NULL OR last_check = 0"
    with get_cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()
