#!/usr/bin/env python3
"""
实验三内容二：写者优先的读者-写者问题
与图2-48的读者优先算法形成对比
"""
import time
import random
from multiprocessing import Process, Lock, Semaphore, Value

# 共享数据
shared_data = "Initial Data"
read_count = Value('i', 0)    # 当前正在读的读者数量
write_count = Value('i', 0)   # 当前正在写或等待的写者数量

# 信号量/锁
mutex_read_count = Lock()     # 保护 read_count
mutex_write_count = Lock()    # 保护 write_count
read_try = Semaphore(1)       # 写者优先的关键：阻止新读者在有写者等待时进入
resource_lock = Lock()        # 保护共享数据的读写锁
service_queue = Semaphore(1)  # （可选）公平队列，防止写者饿死

def reader(reader_id):
    """读者进程"""
    while True: # 模拟无限循环
        # 非临界区：思考
        time.sleep(random.uniform(0.1, 0.5))

        # 写者优先控制：检查是否有写者在等待
        print(f"读者[{reader_id}] 试图进入...")
        read_try.acquire()  # 如果写者已持有read_try，则在此阻塞
        read_try.release()  # 立即释放，允许其他读者尝试

        # 进入临界区，更新读者计数
        with mutex_read_count:
            read_count.value += 1
            if read_count.value == 1:
                # 第一个读者需要获取资源锁，阻止写者
                resource_lock.acquire()
            print(f"  读者[{reader_id}] 进入。当前读者数: {read_count.value}")

        # 读取数据（临界区，但允许多个读者并发）
        print(f"  读者[{reader_id}] 正在读取数据: {shared_data}")
        time.sleep(random.uniform(0.5, 1.0))  # 模拟阅读时间

        # 离开临界区，更新读者计数
        with mutex_read_count:
            read_count.value -= 1
            print(f"  读者[{reader_id}] 离开。当前读者数: {read_count.value}")
            if read_count.value == 0:
                # 最后一个读者离开，释放资源锁，允许写者进入
                resource_lock.release()

        # 非临界区：使用读取的数据
        time.sleep(random.uniform(0.5, 1.0))
        # 为演示清晰，只运行一轮
        break

def writer(writer_id, new_data):
    """写者进程"""
    global shared_data
    # 非临界区：构思数据
    time.sleep(random.uniform(0.1, 0.3))
    print(f"写者[{writer_id}] 准备写入: {new_data}")

    # 更新写者计数，并实现写者优先
    with mutex_write_count:
        write_count.value += 1
        if write_count.value == 1:
            # 第一个写者到来，阻塞后续的新读者
            read_try.acquire()
            print(f"写者[{writer_id}] (第一个) 已阻塞新读者")
        print(f"写者[{writer_id}] 到达。当前写者数: {write_count.value}")

    # 获取资源锁进行写入
    with service_queue:  # 可选的公平队列
        resource_lock.acquire()
        # 写入数据
        print(f"写者[{writer_id}] 开始写入...")
        time.sleep(random.uniform(1.0, 1.5))  # 模拟写入时间
        shared_data = new_data
        print(f"写者[{writer_id}] 写入成功: {shared_data}")
        resource_lock.release()

    # 更新写者计数，并解除对读者的阻塞（如果没有写者了）
    with mutex_write_count:
        write_count.value -= 1
        print(f"写者[{writer_id}] 离开。当前写者数: {write_count.value}")
        if write_count.value == 0:
            # 最后一个写者离开，允许新读者进入
            read_try.release()
            print(f"写者[{writer_id}] (最后一个) 已允许新读者")

def main():
    print("=== 实验三内容二：写者优先的读者-写者问题 ===\n")
    print("对比图2-48的读者优先算法，观察写者如何获得优先权。\n")

    processes = []
    # 创建一个能体现写者优先的测试序列：读者1 -> 读者2 -> 写者1 -> 读者3 -> 写者2
    # 在读者优先中，读者3会直接进入。在写者优先中，读者3会被写者1阻塞。
    test_sequence = [
        ('R', 1), ('R', 2), ('W', 1, "Data by Writer-1"),
        ('R', 3), ('W', 2, "Data by Writer-2")
    ]

    for op in test_sequence:
        time.sleep(0.8)  # 控制进程启动间隔，使输出更清晰
        if op[0] == 'R':
            p = Process(target=reader, args=(op[1],))
        else:
            p = Process(target=writer, args=(op[1], op[2]))
        processes.append(p)
        p.start()

    # 等待所有进程结束
    for p in processes:
        p.join()

    print(f"\n最终共享数据: {shared_data}")

if __name__ == "__main__":
    main()
