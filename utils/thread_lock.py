import threading

# 创建全局锁实例
lock = threading.Lock()

# 提供获取锁和释放锁的方法（可选，直接使用lock.acquire()/release()也可）
def acquire():
    lock.acquire()

def release():
    lock.release()