"""
线程锁包装：提供 with acquire(lock): 的用法，简化锁的获取与释放。

示例：
  with acquire(my_lock):
      # 临界区代码
      do_something()

该实现使用 contextlib.contextmanager，保证异常时也能释放锁，避免死锁。
"""
from contextlib import contextmanager

@contextmanager
def acquire(lock):
    # 获取锁
    lock.acquire()
    try:
        # 在 with 块内执行临界区代码
        yield
    finally:
        # 释放锁，避免死锁
        lock.release()
