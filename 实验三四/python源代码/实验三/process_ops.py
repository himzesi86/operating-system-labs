#!/usr/bin/env python3
"""
实验三：进程管理 - 第一部分
进程基本操作模拟（创建、查看、换出、杀死）
"""
import os
import time
import multiprocessing
import psutil  # 需要安装: pip install psutil
import signal

def worker_child(worker_id):
    """子进程的工作函数"""
    child_pid = os.getpid()
    print(f"   子进程-{worker_id} (PID: {child_pid}) 开始运行...")
    try:
        # 模拟一个长时间运行的任务
        for i in range(30):  # 运行30秒
            print(f"   子进程-{worker_id}: 正在工作... ({i+1}/30)")
            time.sleep(1)
    except KeyboardInterrupt:
        # 当父进程发送终止信号时捕获
        print(f"   子进程-{worker_id} 被中断，正在退出...")
    finally:
        print(f"   子进程-{worker_id} 运行结束。")

def main_process_ops():
    print("=== 实验三：进程基本操作模拟 ===\n")
    
    # 1. 创建新的进程
    print("1. 创建新的进程...")
    processes = []
    for i in range(2):  # 创建2个子进程
        p = multiprocessing.Process(target=worker_child, args=(i+1,))
        p.start()
        processes.append(p)
        print(f"   已创建进程 PID: {p.pid}")
    time.sleep(2)  # 让子进程运行一会儿
    print("   进程创建完成。\n")

    # 2. 查看运行进程
    print("2. 查看运行进程...")
    current_pid = os.getpid()
    print(f"   当前主进程 PID: {current_pid}")
    print("   子进程信息:")
    for i, p in enumerate(processes):
        if p.is_alive():
            print(f"     - 子进程-{i+1}: PID={p.pid}, 状态=运行中")
        else:
            print(f"     - 子进程-{i+1}: PID={p.pid}, 状态=已结束")
    print()

    # 3. 模拟"换出" - 在Linux中可通过`nice`改变优先级，这里模拟暂停/恢复
    print("3. 模拟进程换出（暂停/恢复）...")
    if processes and processes[0].is_alive():
        target_process = psutil.Process(processes[0].pid)
        # 暂停进程 (相当于换出到二级调度)
        target_process.suspend()
        print(f"   已暂停子进程-1 (PID: {processes[0].pid})")
        time.sleep(3)
        # 恢复进程
        target_process.resume()
        print(f"   已恢复子进程-1 (PID: {processes[0].pid})")
    print()

    # 4. 杀死运行进程
    print("4. 杀死运行进程...")
    for i, p in enumerate(processes):
        if p.is_alive():
            p.terminate()  # 发送SIGTERM信号
            p.join(timeout=5)  # 等待进程结束，最多5秒
            if p.exitcode is None:
                print(f"   子进程-{i+1} 正常终止失败，强制杀死...")
                p.kill()  # 发送SIGKILL信号
                p.join()
            print(f"   已杀死子进程-{i+1} (PID: {p.pid})")
        else:
            print(f"   子进程-{i+1} (PID: {p.pid}) 已自然结束。")
    print("\n=== 进程基本操作演示结束 ===\n")
