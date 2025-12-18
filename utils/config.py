import os
from dotenv import load_dotenv

load_dotenv()

def get_mysql_config():
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "db": os.getenv("MYSQL_DB", "blizzard_db"),
        "charset": "utf8mb4",
        "autocommit": False,
    }

def get_account_file_path():
    return os.getenv("ACCOUNT_FILE_PATH", "blizzard_accounts.txt")

def get_separator():
    return os.getenv("SEPARATOR", ":")