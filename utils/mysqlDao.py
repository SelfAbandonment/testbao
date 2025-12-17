"""
MySQL DAO 占位实现：仅打印执行语句，便于本地调试。
真实环境中应连接数据库并执行 SQL。
"""


class Mysql:
    def __init__(self):
        self._closed = False

    def update(self, sql, params):
        """
        执行更新语句（占位）：直接打印 SQL 与参数。
        注意：实际环境需参数化防止 SQL 注入。
        """
        print(f"[MYSQL] EXECUTE: {sql} PARAMS: {params}")

    def dispose(self, close):
        """
        释放连接（占位）：标记已关闭。
        """
        self._closed = True
