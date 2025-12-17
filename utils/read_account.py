"""
账户读取工具
返回包含 cookies 与 BA_tassadar_Cookie_lst 的字典，用于构造 httpx 会话
真实环境应从安全存储或数据库中读取，并避免硬编码
"""

def read_account():
    return {
        'cookies': 'sessionid=8c7992db-4024-44d2-b744-65f4144409c6; locale=en-US',
        'BA_tassadar_Cookie_lst': 'feaeb11b3d80a7fc36c46a77d1b64e9d'
    }
