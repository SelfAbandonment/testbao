"""
内存版 MySQL 操作占位：用于本地调试与跑通流程。
提供 selectOne、updateOneById、selectCount 三个接口，模拟卡数据表。
"""
from threading import Lock

# 模拟的表数据: {table_name: [row, ...]}
_tables = {}
_tables_lock = Lock()

# 保证表存在；若不存在则创建并填充示例数据。
# 字段说明：
# - id: 主键
# - ccnum: 卡号（可能包含空格）
# - expm: 过期月份（字符串）
# - expy: 过期年份（字符串，可能为两位）
# - cvv: 安全码
# - last_check: 最后检查结果（None/1/4/13等占位）
def _ensure_table(name):
    with _tables_lock:
        if name not in _tables:
            # 创建一条测试数据
            _tables[name] = [
                {'id': 1, 'ccnum': '4111 1111 1111 1111', 'expm': '12', 'expy': '30', 'cvv': '123', 'last_check': None},
                {'id': 2, 'ccnum': '4000 0000 0000 0002', 'expm': '1', 'expy': '29', 'cvv': '9', 'last_check': None},
            ]

# selectOne(table_name) 预期返回可迭代的卡片行；代码中通过 `for card in cards:` 进行迭代
def selectOne(table_name):
    _ensure_table(table_name)
    # 实际代码中可能选择一批；这里为了简单起见返回所有。
    return _tables[table_name]

# updateOneById(table_name, last_check, card)
def updateOneById(table_name, last_check, card):
    _ensure_table(table_name)
    with _tables_lock:
        for row in _tables[table_name]:
            if row['id'] == card.get('id'):
                row['last_check'] = last_check
                break

def selectCount(table_name):
    _ensure_table(table_name)
    remaining = len([r for r in _tables[table_name] if r.get('last_check') is None])
    # 返回：列表，包含一个 dict：{'count': 未处理数量}
    return [{'count': remaining}]
