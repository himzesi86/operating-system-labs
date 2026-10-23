class BankersAlgorithm:
    def __init__(self, available, max_resources, allocation):
        self.available = available.copy()
        self.max_resources = [row.copy() for row in max_resources]
        self.allocation = [row.copy() for row in allocation]
        self.need = []
        self.n = len(max_resources)
        self.m = len(available)
        
        for i in range(self.n):
            self.need.append([self.max_resources[i][j] - self.allocation[i][j] for j in range(self.m)])
    
    def is_safe_state(self, available=None, allocation=None, need=None):
        if available is None:
            available = self.available.copy()
        if allocation is None:
            allocation = [row.copy() for row in self.allocation]
        if need is None:
            need = [row.copy() for row in self.need]
            
        work = available.copy()
        finish = [False] * self.n
        safe_sequence = []
        
        while len(safe_sequence) < self.n:
            found = False
            for i in range(self.n):
                if not finish[i] and all(need[i][j] <= work[j] for j in range(self.m)):
                    for j in range(self.m):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(i)
                    found = True
            if not found:
                return False, []
        
        return True, safe_sequence
    
    def request_resources(self, process_id, request):
        if any(request[j] > self.need[process_id][j] for j in range(self.m)):
            return False, "错误：请求超过最大需求"
        
        if any(request[j] > self.available[j] for j in range(self.m)):
            return False, "错误：资源不足"
        
        old_available = self.available.copy()
        old_allocation = [row.copy() for row in self.allocation]
        old_need = [row.copy() for row in self.need]
        
        for j in range(self.m):
            self.available[j] -= request[j]
            self.allocation[process_id][j] += request[j]
            self.need[process_id][j] -= request[j]
        
        is_safe, safe_sequence = self.is_safe_state()
        
        if is_safe:
            return True, safe_sequence
        else:
            self.available = old_available
            self.allocation = old_allocation
            self.need = old_need
            return False, "分配会导致系统不安全"

def main():
    available = [10, 5, 7]
    max_resources = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3]
    ]
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2]
    ]
    
    banker = BankersAlgorithm(available, max_resources, allocation)
    
    is_safe, safe_sequence = banker.is_safe_state()
    print("初始系统状态检查:")
    print(f"系统是否安全: {is_safe}")
    print(f"安全序列: {safe_sequence}")
    print()
    
    print("开始模拟资源请求:")
    print("=" * 50)
    
    requests = [
        (4, [2, 2, 1]),
        (1, [1, 1, 2]),
        (2, [4, 0, 0]),
        (2, [1, 0, 0]),
        (3, [0, 0, 1])
    ]
    
    results = []
    
    for i, (process_id, request) in enumerate(requests):
        is_granted, message = banker.request_resources(process_id, request)
        
        result = {
            'request_num': i + 1,
            'process_id': process_id,
            'request': request,
            'granted': is_granted,
            'message': message,
            'available_after': banker.available.copy() if is_granted else None
        }
        results.append(result)
        
        print(f"请求 {i + 1}: 进程 {process_id} 请求资源 {request}")
        if is_granted:
            print(f"  请求被批准，安全序列: {message}")
        else:
            print(f"  请求被拒绝: {message}")
        print(f"  当前可用资源: {banker.available}")
        print()
    
    with open("banker_algorithm_results.txt", "w") as f:
        f.write("银行家算法模拟结果\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("初始系统状态:\n")
        f.write(f"可用资源: {available}\n")
        f.write("最大需求矩阵:\n")
        for i, row in enumerate(max_resources):
            f.write(f"  进程{i}: {row}\n")
        f.write("当前分配矩阵:\n")
        for i, row in enumerate(allocation):
            f.write(f"  进程{i}: {row}\n")
        f.write(f"初始系统是否安全: {is_safe}\n")
        f.write(f"安全序列: {safe_sequence}\n")
        f.write("\n")
        
        f.write("资源请求处理结果:\n")
        f.write("=" * 30 + "\n")
        for result in results:
            f.write(f"请求 {result['request_num']}:\n")
            f.write(f"  进程 {result['process_id']} 请求资源: {result['request']}\n")
            f.write(f"  是否批准: {'是' if result['granted'] else '否'}\n")
            f.write(f"  详细信息: {result['message']}\n")
            if result['granted']:
                f.write(f"  分配后可用资源: {result['available_after']}\n")
            f.write("\n")

if __name__ == "__main__":
    main()