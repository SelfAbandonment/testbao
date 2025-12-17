# utils/operate_mysql.py
import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

# 数据库配置（需根据实际环境修改）
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'database': 'battle_net',
    'charset': 'utf8mb4',
    'maxconnections': 10  # 连接池最大连接数
}

# 创建连接池
pool = PooledDB(
    creator=pymysql,
    cursorclass=DictCursor,
    **DB_CONFIG
)

# 获取连接
def get_conn():
    return pool.connection()

# 执行SQL（示例）
def execute_sql(sql, args=None):
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, args)
        conn.commit()
        return cursor.rowcount  # 影响的行数
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()