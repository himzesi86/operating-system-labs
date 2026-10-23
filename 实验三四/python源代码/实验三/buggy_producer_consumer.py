#!/usr/bin/env python3
"""
实验三内容三：P101-62题 - 增强版竞争条件演示
增加竞争条件出现概率，确保能观察到题目要求的现象
"""
import threading
import time
import random

# 共享全局变量 - 没有任何保护！
BUFFER_SIZE = 5
buffer = [None] * BUFFER_SIZE
in_index = 0
out_index = 0
count = 0

# 增强的统计和错误检测
program_running = True
errors_detected = []
produced_items = []  # 记录所有生产过的物品
consumed_items = []  # 记录所有消费过的物品

def producer(producer_id):
    """生产者线程 - 增强竞争条件诱发"""
    global in_index, count, buffer, program_running, errors_detected, produced_items
    
    items_produced = 0
    max_items = 50  # 增加生产数量
    
    while items_produced < max_items and program_running:
        # 大幅减少延迟，增加竞争
        time.sleep(random.uniform(0.001, 0.005))
        
        # 检查缓冲区是否满 - 非原子操作！
        check_count = 0
        while count >= BUFFER_SIZE and program_running:  # 修改为>=，更容易触发溢出
            check_count += 1
            if check_count > 3:  # 避免长时间等待
                break
            time.sleep(0.1)
        
        if not program_running:
            break
            
        # !!! 关键修改：大幅增加竞争窗口 !!!
        item = f"P{producer_id}-{items_produced:03d}"
        produced_items.append(item)
        
        # 记录旧的缓冲区值，用于检测覆盖
        old_value = buffer[in_index]
        
        # 非原子操作序列 - 增加中间步骤
        temp_in = in_index
        time.sleep(0.002)  # 增加竞争窗口
        
        # 写入缓冲区
        buffer[temp_in] = item
        time.sleep(0.002)  # 再次增加竞争窗口
        
        # 更新指针 - 非原子！
        in_index = (temp_in + 1) % BUFFER_SIZE
        time.sleep(0.002)
        
        # 关键竞争点：count++ 拆分成多个步骤
        temp_count = count
        time.sleep(0.003)  # 大幅增加竞争窗口
        temp_count += 1
        time.sleep(0.002)
        count = temp_count
        
        items_produced += 1
        
        # 增强错误检测
        if count > BUFFER_SIZE:
            error_msg = f"*** 缓冲区溢出！生产者{producer_id}放入后 count={count} > {BUFFER_SIZE} ***"
            errors_detected.append(error_msg)
            print(error_msg)
        
        if old_value is not None and old_value not in consumed_items:
            error_msg = f"*** 数据覆盖！生产者{producer_id}在位置{temp_in}覆盖了未消费的[{old_value}] ***"
            errors_detected.append(error_msg)
            print(error_msg)
        
        print(f"生产者{producer_id} 放入 [{item}] 到位置 {temp_in}, count={count}")
        
        # 随机延迟
        if random.random() < 0.3:
            time.sleep(0.001)

def consumer(consumer_id):
    """消费者线程 - 增强竞争条件诱发"""
    global out_index, count, buffer, program_running, errors_detected, consumed_items
    
    items_consumed = 0
    max_items = 50  # 增加消费数量
    
    while items_consumed < max_items and program_running:
        time.sleep(random.uniform(0.001, 0.005))
        
        # 检查缓冲区是否空 - 非原子操作！
        check_count = 0
        while count <= 0 and program_running:  # 修改为<=，更容易触发下溢
            check_count += 1
            if check_count > 3 or items_consumed >= max_items:
                break
            time.sleep(0.1)
        
        if not program_running or items_consumed >= max_items:
            break
            
        # !!! 关键修改：大幅增加竞争窗口 !!!
        temp_out = out_index
        time.sleep(0.002)
        
        # 读取缓冲区
        item = buffer[temp_out]
        time.sleep(0.002)
        
        # 清空缓冲区位置（模拟消费）
        buffer[temp_out] = None
        time.sleep(0.002)
        
        # 更新指针
        out_index = (temp_out + 1) % BUFFER_SIZE
        time.sleep(0.002)
        
        # 关键竞争点：count-- 拆分成多个步骤
        temp_count = count
        time.sleep(0.003)  # 大幅增加竞争窗口
        temp_count -= 1
        time.sleep(0.002)
        count = temp_count
        
        items_consumed += 1
        
        if item is not None:
            consumed_items.append(item)
            print(f"消费者{consumer_id} 取出 [{item}] 从位置 {temp_out}, count={count}")
        else:
            error_msg = f"*** 消费空值！消费者{consumer_id} 从位置 {temp_out} 取到None, count={count} ***"
            errors_detected.append(error_msg)
            print(error_msg)
        
        # 增强错误检测
        if count < 0:
            error_msg = f"*** 缓冲区下溢！消费者{consumer_id}取出后 count={count} < 0 ***"
            errors_detected.append(error_msg)
            print(error_msg)
        
        # 随机延迟
        if random.random() < 0.3:
            time.sleep(0.001)

def data_consistency_analysis():
    """详细的数据一致性分析"""
    print("\n" + "="*70)
    print("详细数据一致性分析报告")
    print("="*70)
    
    # 基本统计
    produced_set = set(produced_items)
    consumed_set = set(consumed_items)
    
    print(f"生产物品总数: {len(produced_items)}")
    print(f"消费物品总数: {len(consumed_items)}")
    print(f"唯一生产物品数: {len(produced_set)}")
    print(f"唯一消费物品数: {len(consumed_set)}")
    print(f"最终 count 值: {count} (期望值: 0)")
    print(f"最终 in_index: {in_index}")
    print(f"最终 out_index: {out_index}")
    print(f"缓冲区状态: {buffer}")
    
    # 详细错误分析
    print("\n--- 竞争条件检测结果 ---")
    
    # 1. 检查丢失的物品
    lost_items = produced_set - consumed_set
    if lost_items:
        print(f"*** 发现 {len(lost_items)} 个丢失物品: {list(lost_items)[:5]}... ***")
    else:
        print("✓ 无物品丢失")
    
    # 2. 检查幽灵物品（消费了但未生产）
    phantom_items = consumed_set - produced_set
    if phantom_items:
        print(f"*** 发现 {len(phantom_items)} 个幽灵物品: {list(phantom_items)[:5]}... ***")
    else:
        print("✓ 无幽灵物品")
    
    # 3. 检查重复消费
    from collections import Counter
    item_counts = Counter(consumed_items)
    duplicates = [item for item, count in item_counts.items() if count > 1]
    if duplicates:
        print(f"*** 发现 {len(duplicates)} 个物品被重复消费: {duplicates[:3]}... ***")
    else:
        print("✓ 无重复消费")
    
    # 4. 检查缓冲区计数一致性
    actual_count = sum(1 for item in buffer if item is not None)
    if count != actual_count:
        print(f"*** 计数不一致！count={count}, 实际缓冲区物品数={actual_count} ***")
    else:
        print("✓ 缓冲区计数一致")
    
    # 5. 报告检测到的错误
    if errors_detected:
        print(f"\n*** 运行过程中检测到 {len(errors_detected)} 个竞争条件错误 ***")
        for i, error in enumerate(errors_detected[:3]):  # 显示前3个错误
            print(f"错误{i+1}: {error}")
        if len(errors_detected) > 3:
            print(f"... 还有 {len(errors_detected) - 3} 个错误")
    else:
        print("\n⚠ 本次运行未检测到明显竞争条件错误")
        print("⚠ 竞争条件可能以更隐蔽的形式存在")
    
    return len(errors_detected) > 0 or bool(lost_items or phantom_items or duplicates)

def monitor():
    """增强的监控线程"""
    global program_running
    
    start_time = time.time()
    first_error_time = None
    
    while program_running:
        current_time = time.time() - start_time
        
        # 每5秒报告一次状态
        if int(current_time) % 5 == 0:
            print(f"\n[监控] 运行时间: {current_time:.1f}秒, count={count}, in={in_index}, out={out_index}")
            print(f"[监控] 缓冲区: {buffer}")
            print(f"[监控] 已检测到错误数: {len(errors_detected)}")
        
        # 检测到错误时记录时间
        if errors_detected and first_error_time is None:
            first_error_time = current_time
            print(f"\n[监控] *** 首次检测到竞争条件！用时: {first_error_time:.2f}秒 ***")
        
        # 停止条件：运行20秒或检测到足够多的错误
        if current_time > 20 or (len(errors_detected) >= 3 and current_time > 5):
            print(f"\n[监控] 程序运行结束")
            if first_error_time:
                print(f"[监控] 竞争条件首次出现时间: {first_error_time:.2f}秒")
            program_running = False
            break
            
        time.sleep(0.5)

def main():
    print("=" * 70)
    print("实验三内容三：增强版竞争条件演示")
    print("目的：确保观察到P101-62题要求的竞争条件现象")
    print("=" * 70)
    print()
    
    # 重置全局变量
    global buffer, in_index, out_index, count, program_running, errors_detected
    global produced_items, consumed_items
    buffer = [None] * BUFFER_SIZE
    in_index = out_index = count = 0
    program_running = True
    errors_detected = []
    produced_items = []
    consumed_items = []
    
    print("启动监控线程...")
    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    time.sleep(1)
    
    print("启动4个线程（2生产者 + 2消费者）...")
    print("大幅增加竞争条件出现概率...\n")
    
    # 创建线程
    threads = []
    for i in range(2):
        p = threading.Thread(target=producer, args=(i+1,))
        c = threading.Thread(target=consumer, args=(i+1,))
        threads.extend([p, c])
    
    # 启动所有线程
    start_time = time.time()
    for t in threads:
        t.start()
    
    # 等待所有线程完成
    for t in threads:
        t.join()
    
    total_time = time.time() - start_time
    
    # 详细数据分析
    has_errors = data_consistency_analysis()
    
    print("\n" + "=" * 70)
    print("实验总结")
    print("=" * 70)
    print(f"总运行时间: {total_time:.2f}秒")
    print(f"检测到错误数: {len(errors_detected)}")
    
    if has_errors:
        print("✓ 成功观察到竞争条件！符合题目要求")
        print("✓ 证明了不使用同步原语会导致数据不一致")
    else:
        print("⚠ 未观察到明显竞争条件")
        print("⚠ 建议：调整竞争窗口参数或增加线程数量")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
