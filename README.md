## 依赖安装
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## 配置
在项目根目录创建 `.env`（不要提交到仓库）：
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DB=blizzard_db
ACCOUNT_FILE_PATH=D:\code\gametest\blizzard_accounts.txt
SEPARATOR=:
```

## 数据库表结构示例
```sql
CREATE TABLE blizzard_accounts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  account VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  cookie_text TEXT,
  status TINYINT NOT NULL DEFAULT 0, -- 0 未使用, 1 已使用/成功, 2 失败/失效
  create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  login_time TIMESTAMP NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 脚本
- 初始化导入：`python -m utils.blizzard_db`
- 登录获取 Cookie 并更新：`python -m utils.Cookie`