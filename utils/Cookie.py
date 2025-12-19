import json
import time
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

import pymysql
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from log.log import *
from utils.config import get_mysql_config

MYSQL_GLOBAL_CONFIG = get_mysql_config()

BLIZZARD_LOGIN_URL = "https://account.battle.net/login/en/"
LOGIN_TIMEOUT = 60
VALIDATE_WAIT_TIME = 30
MAX_LOGIN_RETRY = 2  # 登录失败重试次数（总计 1+2 次）
DEFAULT_COOKIE_TTL_HOURS = 2  # 当 Cookie 未提供 expires 时的保守 TTL

def get_mysql_connection(config: dict = None) -> Tuple[Optional[pymysql.connections.Connection], Optional[pymysql.cursors.Cursor]]:
    conn_config = config or MYSQL_GLOBAL_CONFIG
    try:
        conn = pymysql.connect(**conn_config)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor
    except pymysql.OperationalError as e:
        error_code = e.args[0]
        error_msg = e.args[1]
        logger.error(f"❌ MySQL连接失败：{error_msg}（错误码：{error_code}）")
        return None, None
    except Exception as e:
        logger.error(f"❌ MySQL连接异常：{str(e)}")
        return None, None

def execute_single_sql(sql: str, params: tuple = None, conn=None, cursor=None) -> bool:
    owns_conn = False
    if conn is None or cursor is None:
        conn, cursor = get_mysql_connection()
        owns_conn = True
        if not conn or not cursor:
            return False
    try:
        cursor.execute(sql, params or ())
        if sql.strip().upper().startswith(("INSERT", "UPDATE", "ALTER", "CREATE", "DELETE")):
            conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ SQL执行失败：{str(e)}")
        return False
    finally:
        if owns_conn:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

def execute_batch_sql(sql: str, params_list: List[tuple], conn=None, cursor=None) -> int:
    if not params_list:
        return 0
    owns_conn = False
    if conn is None or cursor is None:
        conn, cursor = get_mysql_connection()
        owns_conn = True
        if not conn or not cursor:
            return 0
    try:
        affected_rows = cursor.executemany(sql, params_list)
        conn.commit()
        return affected_rows
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 批量SQL执行失败：{str(e)}")
        return 0
    finally:
        if owns_conn:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

def check_column_exists(table_name: str, column_name: str) -> bool:
    check_sql = """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s; \
                """
    conn, cursor = get_mysql_connection()
    if not conn or not cursor:
        return False
    try:
        cursor.execute(check_sql, (MYSQL_GLOBAL_CONFIG["db"], table_name, column_name))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logger.error(f"❌ 检查字段是否存在失败：{str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_unused_accounts(conn=None, cursor=None) -> List[dict]:
    logger.info("\n===== 开始读取未使用的账户 =====")
    owns = False
    if conn is None or cursor is None:
        conn, cursor = get_mysql_connection()
        owns = True
        if not conn or not cursor:
            return []
    try:
        query_sql = "SELECT id, account, password FROM blizzard_accounts WHERE status = 0;"
        cursor.execute(query_sql)
        accounts = cursor.fetchall()
        logger.info(f"✅ 读取到 {len(accounts)} 个未使用账户")
        return accounts
    except Exception as e:
        logger.error(f"❌ 读取账户失败：{str(e)}")
        return []
    finally:
        if owns:
            cursor.close()
            conn.close()

def compute_expire_at_from_cookies(cookies: List[dict]) -> Optional[datetime]:
    """
    从 cookies 中解析最早的 expires（秒级时间戳）；若无，则给一个保守 TTL。
    """
    expires_list = []
    for c in cookies:
        exp = c.get("expires")
        if exp is None:
            continue
        try:
            exp_ts = float(exp)
            if exp_ts > 0:
                expires_list.append(exp_ts)
        except Exception:
            continue
    if expires_list:
        return datetime.fromtimestamp(min(expires_list))
    # 没有 expires，给保守 TTL
    return datetime.now() + timedelta(hours=DEFAULT_COOKIE_TTL_HOURS)

def login_blizzard(account: str, password: str) -> Tuple[Optional[str], Optional[datetime], str]:
    """
    带重试的登录；返回 (cookie_text, cookie_expire_at, msg)
    """
    last_msg = "未知原因"
    for attempt in range(1 + MAX_LOGIN_RETRY):
        cookie_text, expire_at, msg = _login_once(account, password)
        last_msg = msg
        if cookie_text:
            return cookie_text, expire_at, msg + f"（尝试次数：{attempt+1}）"
        logger.warning(f"⚠️ 登录失败（第{attempt+1}次）：{msg}")
        if attempt < MAX_LOGIN_RETRY:
            time.sleep(5)  # 退避等待
    return None, None, last_msg

def _login_once(account: str, password: str) -> Tuple[Optional[str], Optional[datetime], str]:
    cookie_text = None
    expire_at = None
    msg = "登录成功"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, channel="chrome")
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            page.goto(BLIZZARD_LOGIN_URL, wait_until="networkidle", timeout=LOGIN_TIMEOUT * 1000)

            account_input = page.wait_for_selector('input[name="accountName"]', timeout=15000)
            account_input.fill(account)
            with page.expect_navigation(wait_until="networkidle", timeout=15000):
                page.click('button[type="submit"]', timeout=15000)

            password_input = page.wait_for_selector('input[name="password"]', timeout=15000)
            password_input.fill(password)
            with page.expect_navigation(wait_until="networkidle", timeout=20000):
                page.click('button[type="submit"]', timeout=15000)

            logger.warning(f"🔍 账户 {account} 登录中，若出现人机验证请在{VALIDATE_WAIT_TIME}秒内完成...")
            time.sleep(VALIDATE_WAIT_TIME)

            current_url = page.url
            if ("overview" in current_url) or ("/account.battle.net/" in current_url and "login" not in current_url):
                cookies = context.cookies()
                expire_at = compute_expire_at_from_cookies(cookies)
                cookie_text = json.dumps(cookies, ensure_ascii=False, indent=2)
                msg = "登录成功"
                logger.info(f"✅ 账户 {account} 登录成功")
            else:
                msg = f"登录失败：未跳转到概览页（当前URL：{current_url[:120]}）"
                cookie_text = None
                expire_at = None
    except PlaywrightTimeoutError:
        msg = "登录超时（导航/元素加载超时，可能人机验证未完成）"
    except Exception as e:
        if "Execution context was destroyed" in str(e):
            msg = "登录异常：页面导航导致执行上下文销毁"
        else:
            msg = f"登录异常：{str(e)[:200]}"
    return cookie_text, expire_at, msg

def update_account_status(account_id: int, cookie_text: Optional[str], status: int, conn=None, cursor=None, cookie_expire_at: Optional[datetime] = None):
    """
    更新单个账户的 Cookie、登录时间、状态、过期时间、最近检查时间
    """
    update_sql = """
                 UPDATE blizzard_accounts
                 SET
                     cookie_text = %s,
                     login_time = %s,
                     status = %s,
                     cookie_expire_at = %s,
                     last_check_at = %s
                 WHERE id = %s; \
                 """
    now = datetime.now()
    login_time = now if cookie_text else None
    params = (cookie_text, login_time, status, cookie_expire_at, now, account_id)
    if execute_single_sql(update_sql, params, conn=conn, cursor=cursor):
        status_desc = "已使用" if status == 1 else "失效"
        logger.info(f"✅ 账户ID {account_id} 状态更新为「{status_desc}」")
    else:
        logger.error(f"❌ 账户ID {account_id} 状态更新失败")

def mark_expired_accounts(conn=None, cursor=None):
    """
    将已过期的 status=1 账号置为 status=2，并清空 Cookie。
    """
    sql = """
          UPDATE blizzard_accounts
          SET status = 2,
              cookie_text = NULL,
              cookie_expire_at = NULL,
              last_check_at = NOW()
          WHERE status = 1
            AND cookie_expire_at IS NOT NULL
            AND cookie_expire_at <= NOW(); \
          """
    execute_single_sql(sql, conn=conn, cursor=cursor)

def main():
    start_time = datetime.now()
    logger.info(f"===== 暴雪账户登录并更新Cookie脚本启动（{start_time.strftime('%Y-%m-%d %H:%M:%S')}）=====")

    conn, cursor = get_mysql_connection()
    if not conn or not cursor:
        return

    try:
        # 先将已过期的可用账号置为失效
        mark_expired_accounts(conn=conn, cursor=cursor)

        unused_accounts = get_unused_accounts(conn=conn, cursor=cursor)
        if not unused_accounts:
            logger.warning("⚠️ 无未使用的账户，脚本结束")
            return

        for account in unused_accounts:
            account_id = account["id"]
            account_name = account["account"]
            account_pwd = account["password"]

            logger.info(f"\n===== 处理账户：{account_name} =====")
            cookie_text, expire_at, msg = login_blizzard(account_name, account_pwd)
            logger.info(f"📝 {msg}")

            if cookie_text:
                update_account_status(account_id, cookie_text, 1, conn=conn, cursor=cursor, cookie_expire_at=expire_at)
            else:
                update_account_status(account_id, None, 2, conn=conn, cursor=cursor, cookie_expire_at=None)
    finally:
        cursor.close()
        conn.close()

    end_time = datetime.now()
    logger.info(f"\n===== 脚本执行完成（耗时：{end_time - start_time}）=====")

if __name__ == "__main__":
    main()