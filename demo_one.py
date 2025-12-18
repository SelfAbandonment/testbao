from playwright.sync_api import sync_playwright
import time
import pymysql
import json
from typing import List, Optional
from log.log import *  # 若无需日志可注释，或替换为print

# MySQL连接配置（复用之前的配置）
MYSQL_GLOBAL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "ypXZQGkKg0mp4gdQ",
    "db": "blizzard_db",
    "charset": "utf8mb4",
    "autocommit": False
}

def get_mysql_connection():
    """获取MySQL连接和游标（字典游标）"""
    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**MYSQL_GLOBAL_CONFIG)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        logger.info("✅ MySQL连接成功")
        return conn, cursor
    except pymysql.OperationalError as e:
        error_code, error_msg = e.args
        logger.error(f"❌ MySQL连接失败：{error_msg}（错误码：{error_code}）")
        return None, None
    except Exception as e:
        logger.error(f"❌ MySQL连接异常：{str(e)}")
        return None, None

def get_valid_cookies_from_db() -> Optional[List[dict]]:
    """
    从数据库读取status=1的账户的cookie_text字段（JSON格式）
    :return: 解析后的Cookie列表，无有效数据返回None
    """
    # 1. 建立数据库连接
    conn, cursor = get_mysql_connection()
    if not conn or not cursor:
        return None

    try:
        # 2. 查询status=1的第一条有效Cookie（可根据需求调整为指定账户）
        query_sql = """
                    SELECT cookie_text
                    FROM blizzard_accounts
                    WHERE status = 1 AND cookie_text IS NOT NULL AND cookie_text != ''
                    LIMIT 1; \
                    """
        cursor.execute(query_sql)
        result = cursor.fetchone()

        if not result:
            logger.warning("⚠️ 数据库中无status=1的有效Cookie（未找到登录成功的账户）")
            return None

        # 3. 解析JSON格式的Cookie文本
        cookie_text = result["cookie_text"]
        try:
            cookies = json.loads(cookie_text)
            # 验证解析结果是列表且包含必要字段
            if not isinstance(cookies, list) or len(cookies) == 0:
                logger.error("❌ Cookie解析失败：不是有效列表格式")
                return None
            # 补充Cookie的domain/path（防止部分Cookie缺失关键字段）
            for cookie in cookies:
                if "domain" not in cookie or not cookie["domain"]:
                    cookie["domain"] = ".battle.net"
                if "path" not in cookie or not cookie["path"]:
                    cookie["path"] = "/"
            logger.info(f"✅ 成功读取并解析Cookie，共{len(cookies)}条")
            return cookies
        except json.JSONDecodeError as e:
            logger.error(f"❌ Cookie JSON解析失败：{str(e)}")
            return None

    except Exception as e:
        logger.error(f"❌ 查询数据库Cookie失败：{str(e)}")
        return None
    finally:
        # 4. 关闭连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_battlenet_page():
    """使用数据库中的Cookie访问战网概览页"""
    # 第一步：从数据库获取有效Cookie
    cookies = get_valid_cookies_from_db()
    if not cookies:
        logger.error("❌ 无有效Cookie，终止执行")
        return

    # 第二步：使用Playwright加载Cookie并访问页面
    try:
        with sync_playwright() as p:
            # 启动Chrome浏览器（headless=False显示界面）
            browser = p.chromium.launch(headless=False, channel="chrome")
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
                viewport={"width": 1920, "height": 1080}  # 避免元素遮挡
            )

            # 先访问战网域名（建立Cookie上下文）
            page = context.new_page()
            logger.info("📌 正在访问战网基础域名...")
            page.goto("https://account.battle.net", wait_until="domcontentloaded", timeout=60000)

            # 添加从数据库读取的Cookie
            logger.info("📌 正在添加数据库中的Cookie...")
            context.add_cookies(cookies)

            # 访问目标页面（概览页）
            logger.info("📌 正在访问战网概览页...")
            page.goto("https://account.battle.net/overview", wait_until="networkidle", timeout=60000)

            # 等待页面稳定/手动验证（如有需要）
            logger.warning("🔍 页面加载完成，等待15秒（可手动验证登录状态）...")
            time.sleep(15)

            # 保存截图验证登录结果
            screenshot_path = "battlenet_overview.png"
            page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"✅ 页面截图已保存至：{screenshot_path}")

            # 可选：打印页面标题，验证是否登录成功
            page_title = page.title()
            logger.info(f"📄 页面标题：{page_title}")

            # 关闭浏览器
            browser.close()
            logger.info("✅ 操作完成，浏览器已关闭")

    except Exception as e:
        logger.error(f"❌ Playwright执行异常：{str(e)}")

if __name__ == "__main__":
    logger.info("===== 开始执行战网Cookie访问脚本 =====")
    get_battlenet_page()
    logger.info("===== 脚本执行结束 =====")