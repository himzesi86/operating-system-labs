#!/usr/bin/env python3
"""
实验四第一部分：信号通信
多进程使用信号进行通信
"""
import os
import signal
import time
import sys
from multiprocessing import Process, current_process

# 自定义信号处理状态
signal_received = False
received_signals = []

def child_signal_handler(signum, frame):
    """子进程信号处理函数"""
    global signal_received, received_signals
    signal_received = True
    received_signals.append(signum)
    process_name = current_process().name
    print(f"[{process_name}] 接收到信号: {signum} ({signal.Signals(signum).name})")
    
    # 回应父进程
    if signum == signal.SIGUSR1:
        parent_pid = os.getppid()
        print(f"[{process_name}] 向父进程 {parent_pid} 发送 SIGUSR2 作为回应")
        os.kill(parent_pid, signal.SIGUSR2)

def parent_signal_handler(signum, frame):
    """父进程信号处理函数"""
    print(f"[父进程] 接收到子进程回应信号: {signum} ({signal.Signals(signum).name})")

def child_process():
    """子进程函数"""
    process_name = current_process().name
    print(f"[{process_name}] 子进程启动，PID: {os.getpid()}, 父进程PID: {os.getppid()}")
    
    # 注册信号处理函数
    signal.signal(signal.SIGUSR1, child_signal_handler)
    signal.signal(signal.SIGUSR2, child_signal_handler)
    
    print(f"[{process_name}] 等待接收信号...")
    
    # 等待信号
    timeout = 10  # 10秒超时
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if signal_received:
            print(f"[{process_name}] 成功完成信号通信")
            break
        time.sleep(0.1)
    else:
        print(f"[{process_name}] 等待超时")
    
    print(f"[{process_name}] 子进程退出，共接收 {len(received_signals)} 个信号")

def signal_communication_example():
    """信号通信主函数"""
    print("=" * 60)
    print("实验四第一部分：信号通信")
    print("=" * 60)
    
    # 注册父进程信号处理
    signal.signal(signal.SIGUSR2, parent_signal_handler)
    
    # 创建子进程
    child = Process(target=child_process, name="子进程")
    child.start()
    
    # 给子进程一些启动时间
    time.sleep(1)
    
    print(f"[父进程] 父进程PID: {os.getpid()}, 子进程PID: {child.pid}")
    
    # 向子进程发送信号
    signals_to_send = [signal.SIGUSR1, signal.SIGUSR2]
    
    for i, sig in enumerate(signals_to_send):
        print(f"[父进程] 第{i+1}次向子进程发送信号: {sig} ({signal.Signals(sig).name})")
        os.kill(child.pid, sig)
        time.sleep(1)  # 等待子进程处理
    
    # 等待子进程结束
    child.join(timeout=5)
    
    if child.is_alive():
        print("[父进程] 子进程未正常结束，强制终止")
        child.terminate()
    
    print("[父进程] 信号通信示例完成\n")

if __name__ == "__main__":
    signal_communication_example()
