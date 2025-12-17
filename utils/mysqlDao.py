# utils/mysqlDao.py
from .operate_mysql import execute_sql, get_conn

# 示例：查询账号信息（假设存在account表）
def get_accounts(limit=10):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, password FROM account LIMIT %s", (limit,))
        return cursor.fetchall()  # 返回字典列表
    finally:
        cursor.close()
        conn.close()

# 示例：插入操作结果
def insert_result(account_id, status, message):
    sql = """
          INSERT INTO operation_result (account_id, status, message, create_time)
          VALUES (%s, %s, %s, NOW()) \
          """
    return execute_sql(sql, (account_id, status, message))