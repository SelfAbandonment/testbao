import pymysql
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json
from typing import List, Tuple, Optional
import time
from log.log import *
from datetime import datetime

# MySQL连接配置
MYSQL_GLOBAL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "ypXZQGkKg0mp4gdQ",
    "db": "blizzard_db",
    "charset": "utf8mb4",
    "autocommit": False
}

# 暴雪登录相关配置
BLIZZARD_LOGIN_URL = "https://account.battle.net/login/en/"
LOGIN_TIMEOUT = 60
VALIDATE_WAIT_TIME = 30

def get_mysql_connection(config: dict = None) -> Tuple[Optional[pymysql.connections.Connection], Optional[pymysql.cursors.Cursor]]:
    conn_config = config or MYSQL_GLOBAL_CONFIG
    conn = None
    cursor = None
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

def execute_single_sql(sql: str, params: tuple = None, config: dict = None) -> bool:
    conn, cursor = get_mysql_connection(config)
    if not conn or not cursor:
        return False
    try:
        cursor.execute(sql, params or ())
        if sql.strip().upper().startswith(("INSERT", "UPDATE", "ALTER", "CREATE")):
            conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ SQL执行失败：{str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_batch_sql(sql: str, params_list: List[tuple], config: dict = None) -> int:
    if not params_list:
        return 0
    conn, cursor = get_mysql_connection(config)
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def check_column_exists(table_name: str, column_name: str) -> bool:
    """
    检查指定表是否存在指定字段（兼容所有MySQL版本，彻底清理多余符号）
    """
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_unused_accounts() -> List[dict]:
    """
    从数据库读取status=0（未使用）的账户列表
    """
    logger.info("\n===== 开始读取未使用的账户 =====")
    query_sql = "SELECT id, account, password FROM blizzard_accounts WHERE status = 0;"
    conn, cursor = get_mysql_connection()
    if not conn or not cursor:
        return []

    try:
        cursor.execute(query_sql)
        accounts = cursor.fetchall()
        logger.info(f"✅ 读取到 {len(accounts)} 个未使用账户")
        return accounts
    except Exception as e:
        logger.error(f"❌ 读取账户失败：{str(e)}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def login_blizzard(account: str, password: str) -> Tuple[Optional[str], str]:
    """
    模拟登录暴雪账户（适配分步登录流程：账户页→密码页）
    解决：执行上下文销毁、导航异常问题
    """
    cookie_text = None
    msg = "登录成功"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, channel="chrome")
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                # 增加视口大小，避免元素被遮挡
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()

            # 步骤1：访问登录页，等待页面稳定
            page.goto(BLIZZARD_LOGIN_URL, wait_until="networkidle", timeout=LOGIN_TIMEOUT * 1000)

            # 步骤2：处理第一步（输入账户名）
            logger.info(f"📌 正在输入账户名：{account}")
            account_input = page.wait_for_selector('input[name="accountName"]', timeout=15000)
            account_input.fill(account)

            # 点击提交，等待页面导航（跳转到密码页）
            with page.expect_navigation(wait_until="networkidle", timeout=15000):
                page.click('button[type="submit"]', timeout=15000)

            # 步骤3：处理第二步（输入密码）
            logger.info(f"📌 正在输入密码")
            password_input = page.wait_for_selector('input[name="password"]', timeout=15000)
            password_input.fill(password)

            # 点击提交，等待登录结果导航
            logger.info(f"📌 提交登录信息")
            with page.expect_navigation(wait_until="networkidle", timeout=15000):
                page.click('button[type="submit"]', timeout=15000)

            # 步骤4：等待人机验证/登录结果（延长等待时间，适配验证）
            logger.warning(f"🔍 账户 {account} 登录中，若出现人机验证请在{VALIDATE_WAIT_TIME}秒内完成...")
            time.sleep(VALIDATE_WAIT_TIME)

            # 步骤5：判断登录结果（优先检查URL，避免查询元素触发上下文错误）
            current_url = page.url
            if "overview" in current_url or ("/account/battle.net/" in current_url and "login" not in current_url):
                # 登录成功，获取Cookie
                cookies = context.cookies()
                cookie_text = json.dumps(cookies, ensure_ascii=False, indent=2)
                msg = "登录成功"
                logger.info(f"✅ 账户 {account} 登录成功")
            else:
                # 登录失败，不查询元素（避免上下文错误），直接根据URL判断
                msg = f"登录失败：页面未跳转到概览页（当前URL：{current_url[:100]}）"
                cookie_text = None

    except PlaywrightTimeoutError:
        msg = "登录超时（页面导航/元素加载超时，可能是人机验证未完成）"
    except Exception as e:
        # 捕获上下文销毁异常，友好提示
        if "Execution context was destroyed" in str(e):
            msg = "登录异常：页面导航导致执行上下文销毁（分步登录流程未适配）"
        else:
            msg = f"登录异常：{str(e)[:200]}"  # 截断过长的异常信息

    return cookie_text, msg

def update_account_status(account_id: int, cookie_text: Optional[str], status: int):
    """
    更新单个账户的Cookie、登录时间、状态（彻底清理所有多余符号）
    """
    update_sql = """
                 UPDATE blizzard_accounts
                 SET
                     cookie_text = %s,
                     login_time = %s,
                     status = %s
                 WHERE id = %s; \
                 """
    login_time = datetime.now() if cookie_text else None
    params = (cookie_text, login_time, status, account_id)

    if execute_single_sql(update_sql, params):
        status_desc = "已使用" if status == 1 else "失效"
        logger.info(f"✅ 账户ID {account_id} 状态更新为「{status_desc}」")
    else:
        logger.error(f"❌ 账户ID {account_id} 状态更新失败")

def main():
    start_time = datetime.now()
    logger.info(f"===== 暴雪账户登录并更新Cookie脚本启动（{start_time.strftime('%Y-%m-%d %H:%M:%S')}）=====")

    # 读取未使用账户
    unused_accounts = get_unused_accounts()
    if not unused_accounts:
        logger.warning("⚠️ 无未使用的账户，脚本结束")
        return

    # 遍历登录并更新
    for account in unused_accounts:
        account_id = account["id"]
        account_name = account["account"]
        account_pwd = account["password"]

        logger.info(f"\n===== 处理账户：{account_name} =====")
        cookie_text, msg = login_blizzard(account_name, account_pwd)
        logger.info(f"📝 {msg}")

        # 更新状态
        if cookie_text:
            update_account_status(account_id, cookie_text, 1)
        else:
            update_account_status(account_id, None, 2)

    end_time = datetime.now()
    logger.info(f"\n===== 脚本执行完成（耗时：{end_time - start_time}）=====")

if __name__ == "__main__":
    main()