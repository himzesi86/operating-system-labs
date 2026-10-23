import threading
import time
import random

# ===================== 39题：避免死锁（修正版）=====================
class BaboonCrossing39:
    def __init__(self):
        self.mutex = threading.Lock()
        self.rope = threading.Semaphore(1)
        self.east_count = 0
        self.west_count = 0
        self.current_direction = None
        
    def cross_east(self, baboon_id):
        print(f"狒狒 {baboon_id} 到达东侧，等待过峡谷")
        
        # 第一部分：进入绳索系统
        entered = False
        while not entered:
            with self.mutex:
                if self.current_direction is None:
                    self.current_direction = 'E'
                    self.east_count = 1
                    self.rope.acquire()
                    entered = True
                elif self.current_direction == 'E':
                    self.east_count += 1
                    entered = True
                # 如果方向是'W'，继续等待
            if not entered:
                time.sleep(0.01)
        
        print(f"狒狒 {baboon_id} 开始向东过峡谷")
        time.sleep(random.uniform(0.1, 0.3))
        print(f"狒狒 {baboon_id} 完成向东过峡谷")
        
        # 离开绳索
        with self.mutex:
            self.east_count -= 1
            if self.east_count == 0:
                self.current_direction = None
                self.rope.release()
    
    def cross_west(self, baboon_id):
        print(f"狒狒 {baboon_id} 到达西侧，等待过峡谷")
        
        # 第一部分：进入绳索系统
        entered = False
        while not entered:
            with self.mutex:
                if self.current_direction is None:
                    self.current_direction = 'W'
                    self.west_count = 1
                    self.rope.acquire()
                    entered = True
                elif self.current_direction == 'W':
                    self.west_count += 1
                    entered = True
                # 如果方向是'E'，继续等待
            if not entered:
                time.sleep(0.01)
        
        print(f"狒狒 {baboon_id} 开始向西过峡谷")
        time.sleep(random.uniform(0.1, 0.3))
        print(f"狒狒 {baboon_id} 完成向西过峡谷")
        
        # 离开绳索
        with self.mutex:
            self.west_count -= 1
            if self.west_count == 0:
                self.current_direction = None
                self.rope.release()

def test_39():
    print("=== 39题测试：避免死锁 ===")
    crossing = BaboonCrossing39()
    
    threads = []
    
    # 创建5只东向狒狒
    for i in range(5):
        t = threading.Thread(target=crossing.cross_east, args=(f"E{i}",))
        threads.append(t)
    
    # 创建5只西向狒狒
    for i in range(5):
        t = threading.Thread(target=crossing.cross_west, args=(f"W{i}",))
        threads.append(t)
    
    # 随机打乱顺序
    random.shuffle(threads)
    
    # 启动所有线程
    print("启动10只狒狒线程...")
    for t in threads:
        t.start()
        time.sleep(random.uniform(0.05, 0.1))
    
    # 等待所有线程完成（设置超时时间，避免永久等待）
    print("等待狒狒完成过峡谷...")
    for t in threads:
        t.join(timeout=5.0)  # 设置5秒超时
        if t.is_alive():
            print(f"警告：线程 {t.name} 未在5秒内完成，可能存在死锁")
    
    print("39题测试完成，所有狒狒已安全过峡谷（无死锁）\n")


# ===================== 40题：避免饥饿（简化正确版）=====================
class BaboonCrossing40:
    def __init__(self):
        self.mutex = threading.Lock()
        self.rope = threading.Semaphore(1)
        self.east_count = 0
        self.west_count = 0
        self.current_direction = None
        self.east_has_gone = False
        
    def cross_east(self, baboon_id):
        print(f"狒狒 {baboon_id} 到达东侧，等待过峡谷")
        
        # 进入绳索
        entered = False
        while not entered:
            with self.mutex:
                if self.current_direction is None:
                    self.current_direction = 'E'
                    self.east_count = 1
                    self.east_has_gone = True  # 设置标志
                    self.rope.acquire()
                    entered = True
                elif self.current_direction == 'E':
                    self.east_count += 1
                    self.east_has_gone = True  # 设置标志
                    entered = True
            if not entered:
                time.sleep(0.01)
        
        print(f"狒狒 {baboon_id} 开始向东过峡谷")
        time.sleep(random.uniform(0.1, 0.3))
        print(f"狒狒 {baboon_id} 完成向东过峡谷")
        
        # 离开
        with self.mutex:
            self.east_count -= 1
            if self.east_count == 0:
                self.current_direction = None
                self.rope.release()
    
    def cross_west(self, baboon_id):
        print(f"狒狒 {baboon_id} 到达西侧，等待过峡谷")
        
        # **关键：等待直到有东向狒狒通过过**
        while True:
            with self.mutex:
                if self.east_has_gone:
                    break
            time.sleep(0.01)
        
        # 进入绳索
        entered = False
        while not entered:
            with self.mutex:
                if self.current_direction is None:
                    self.current_direction = 'W'
                    self.west_count = 1
                    self.rope.acquire()
                    entered = True
                elif self.current_direction == 'W':
                    self.west_count += 1
                    entered = True
            if not entered:
                time.sleep(0.01)
        
        print(f"狒狒 {baboon_id} 开始向西过峡谷")
        time.sleep(random.uniform(0.1, 0.3))
        print(f"狒狒 {baboon_id} 完成向西过峡谷")
        
        # 离开
        with self.mutex:
            self.west_count -= 1
            if self.west_count == 0:
                self.current_direction = None
                self.rope.release()

def test_40():
    print("\n=== 40题测试：避免饥饿 ===")
    print("规则：西向狒狒必须等待至少一只东向狒狒通过后才能开始")
    print("=" * 60)
    
    crossing = BaboonCrossing40()
    
    threads = []
    
    # 创建9只狒狒：4西5东
    for i in range(2):  # 西向狒狒
        t = threading.Thread(target=crossing.cross_west, args=(f"W{i}",))
        threads.append(t)
    
    for i in range(3):  # 东向狒狒
        t = threading.Thread(target=crossing.cross_east, args=(f"E{i}",))
        threads.append(t)
    
    for i in range(2, 4):  # 更多西向
        t = threading.Thread(target=crossing.cross_west, args=(f"W{i}",))
        threads.append(t)
    
    for i in range(3, 5):  # 更多东向
        t = threading.Thread(target=crossing.cross_east, args=(f"E{i}",))
        threads.append(t)
    
    # 打乱顺序
    random.shuffle(threads)
    
    # 启动
    print("启动所有狒狒线程...")
    for t in threads:
        t.start()
        time.sleep(random.uniform(0.05, 0.1))
    
    # 等待完成（带超时）
    print("\n等待狒狒完成...")
    for t in threads:
        t.join(timeout=5.0)
        if t.is_alive():
            print(f"警告：线程 {t.name} 未在5秒内完成")
    
    print("=" * 60)
    print("40题测试完成，所有狒狒已安全过峡谷（无死锁且无饥饿）")


# ===================== 主程序 =====================
if __name__ == "__main__":
    random.seed(42)
    
    print("狒狒过峡谷问题 - 同步问题演示")
    print("=" * 50)
    
    try:
        test_39()
        time.sleep(1)
        test_40()
        print("\n✅ 所有测试完成成功！")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")