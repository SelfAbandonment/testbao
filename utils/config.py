from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    account_source: str = os.getenv('ACCOUNT_SOURCE', 'file')
    account_file: str = os.getenv('ACCOUNT_FILE', 'accounts.json')
    proxy_url: str | None = os.getenv('HTTP_PROXY')
    http_user_agent: str = os.getenv('HTTP_USER_AGENT', 'Mozilla/5.0')
    default_table: str = os.getenv('CARD_TABLE', 'cards')


settings = Settings()

