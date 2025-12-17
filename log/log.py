from datetime import datetime

"""
日志工具：提供统一的控制台输出，标注时间与级别
"""
class _Logger:
    def _fmt(self, level, msg):
        # 统一格式：时间戳 + 级别 + 信息
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{ts}] {level}: {msg}"

    def debug(self, msg):
        # 调试信息
        print(self._fmt('DEBUG', msg))

    def info(self, msg):
        # 一般信息
        print(self._fmt('INFO', msg))

    def error(self, msg):
        # 错误信息
        print(self._fmt('ERROR', msg))

    def success(self, msg):
        # 成功信息
        print(self._fmt('SUCCESS', msg))


# 全局 logger 实例，供外部直接使用
logger = _Logger()