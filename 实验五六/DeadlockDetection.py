class DeadlockDetector:
    def __init__(self):
        # 测试数据集合
        self.test_cases = {
            'safe_case': self._get_safe_case(),
            'deadlock_case': self._get_deadlock_case(),
            'another_safe_case': self._get_another_safe_case(),
            'complex_deadlock_case': self._get_complex_deadlock_case()
        }
    
    def _get_safe_case(self):
        """安全情况测试数据"""
        return {
            'name': '安全情况',
            'available': [3, 3, 2],
            'max_demand': [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 2],
                [2, 2, 2],
                [4, 3, 3]
            ],
            'allocation': [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 2],
                [2, 1, 1],
                [0, 0, 2]
            ]
        }
    
    def _get_deadlock_case(self):
        """死锁情况测试数据"""
        return {
            'name': '死锁情况',
            'available': [0, 0, 0],
            'max_demand': [
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1]
            ],
            'allocation': [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]
            ]
        }
    
    def _get_another_safe_case(self):
        """另一个安全情况"""
        return {
            'name': '另一个安全情况',
            'available': [2, 1, 0],
            'max_demand': [
                [3, 2, 1],
                [2, 1, 1],
                [4, 2, 2]
            ],
            'allocation': [
                [1, 1, 1],
                [0, 0, 0],
                [1, 0, 1]
            ]
        }
    
    def _get_complex_deadlock_case(self):
        """复杂死锁情况"""
        return {
            'name': '复杂死锁情况',
            'available': [1, 0, 2],
            'max_demand': [
                [2, 2, 3],
                [3, 1, 2],
                [2, 2, 2],
                [1, 1, 1]
            ],
            'allocation': [
                [1, 2, 1],
                [2, 1, 0],
                [0, 0, 1],
                [0, 0, 0]
            ]
        }
    
    def detect_single_instance(self):
        """单实例资源死锁检测"""
        print("=== 单实例资源死锁检测 ===")
        
        # 测试数据 - 存在死锁
        allocation = {
            'P0': ['R1'],
            'P1': ['R2'],
            'P2': ['R3'],
            'P3': ['R0']
        }
        request = {
            'P0': ['R2'],
            'P1': ['R3'],
            'P2': ['R0'],
            'P3': ['R1']
        }
        
        # 构建资源分配图
        graph = {}
        for process in allocation:
            graph[process] = []
        
        # 添加请求边
        for process, resources in request.items():
            for resource in resources:
                for holder, held_resources in allocation.items():
                    if resource in held_resources:
                        graph[process].append(holder)
        
        print("资源分配图:")
        for process, dependencies in graph.items():
            print(f"{process} -> {dependencies}")
        
        # 检测环路
        deadlock = self._detect_cycle(graph)
        
        if deadlock:
            print("❌ 检测到死锁！存在环路")
            print(f"死锁进程: {deadlock}")
        else:
            print("✅ 系统安全，无死锁")
        
        print("\n" + "="*50 + "\n")
    
    def _detect_cycle(self, graph):
        """检测图中环路"""
        visited = set()
        recursion_stack = set()
        
        def dfs(node, path):
            if node in recursion_stack:
                cycle_start = path.index(node)
                return path[cycle_start:]
            
            if node in visited:
                return None
            
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                result = dfs(neighbor, path.copy())
                if result:
                    return result
            
            recursion_stack.remove(node)
            path.pop()
            return None
        
        for node in graph:
            result = dfs(node, [])
            if result:
                return result
        
        return None
    
    def detect_multi_instance(self, test_case):
        """多实例资源死锁检测（银行家算法）"""
        print(f"=== 多实例资源死锁检测 - {test_case['name']} ===")
        
        available = test_case['available']
        max_demand = test_case['max_demand']
        allocation = test_case['allocation']
        
        n = len(max_demand)  # 进程数
        m = len(available)   # 资源类型数
        
        # 计算需求矩阵
        need = []
        for i in range(n):
            need_i = [max_demand[i][j] - allocation[i][j] for j in range(m)]
            need.append(need_i)
        
        print("当前资源分配情况:")
        print("进程\t最大需求\t已分配\t需求")
        for i in range(n):
            print(f"P{i}\t{max_demand[i]}\t{allocation[i]}\t{need[i]}")
        print(f"可用资源: {available}")
        
        # 银行家算法检测安全性
        work = available.copy()
        finish = [False] * n
        safe_sequence = []
        
        print("\n资源分配过程:")
        iteration = 0
        while len(safe_sequence) < n:
            iteration += 1
            found = False
            
            for i in range(n):
                if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                    # 进程i的需求可以被满足
                    print(f"第{iteration}轮: P{i} 的需求 {need[i]} <= 可用资源 {work} ✓")
                    
                    # 模拟进程执行完成，释放资源
                    for j in range(m):
                        work[j] += allocation[i][j]
                    
                    finish[i] = True
                    safe_sequence.append(f"P{i}")
                    found = True
                    print(f"      P{i} 执行完成，释放资源 {allocation[i]}")
                    print(f"      可用资源变为: {work}")
                    break
                elif not finish[i]:
                    print(f"第{iteration}轮: P{i} 的需求 {need[i]} > 可用资源 {work} ✗")
            
            if not found:
                print(f"第{iteration}轮: 找不到可以满足需求的进程")
                break
        
        # 结果判断
        if len(safe_sequence) == n:
            print(f"\n✅ 系统处于安全状态")
            print(f"安全序列: {' -> '.join(safe_sequence)}")
        else:
            deadlock_processes = [f"P{i}" for i in range(n) if not finish[i]]
            print(f"\n❌ 系统处于不安全状态，发生死锁！")
            print(f"死锁进程: {deadlock_processes}")
            print(f"已完成进程: {safe_sequence}")
        
        print("\n" + "="*50 + "\n")
        return len(safe_sequence) == n
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("死锁检测系统 - 多实例资源测试")
        print("="*60)
        
        # 单实例检测
        self.detect_single_instance()
        
        # 多实例检测 - 各种情况
        results = {}
        for case_name, test_case in self.test_cases.items():
            results[case_name] = self.detect_multi_instance(test_case)
        
        # 统计结果
        print("=== 测试结果汇总 ===")
        safe_count = sum(1 for result in results.values() if result)
        deadlock_count = len(results) - safe_count
        
        print(f"安全情况: {safe_count} 个")
        print(f"死锁情况: {deadlock_count} 个")
        
        for case_name, is_safe in results.items():
            status = "安全" if is_safe else "死锁"
            print(f"{self.test_cases[case_name]['name']}: {status}")

# 运行检测
if __name__ == "__main__":
    detector = DeadlockDetector()
    detector.run_all_tests()