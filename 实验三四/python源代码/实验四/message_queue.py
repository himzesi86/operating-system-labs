import os
import time
from multiprocessing import Process, Queue
import random

class MessageType:
    GREETING = 1
    DATA_REQUEST = 2
    DATA_RESPONSE = 3
    EXIT = 4

def server(queue):
    print(f"服务进程 {os.getpid()} 启动，等待消息...")
    client_count = 0
    random.seed(42)
    
    while True:
        try:
            msg = queue.get(timeout=10)
            
            if msg['type'] == MessageType.GREETING:
                client_count += 1
                print(f"服务进程收到问候来自客户端 {msg['client_id']}")
                
                response = {
                    'type': MessageType.DATA_REQUEST,
                    'server_id': os.getpid(),
                    'message': f"Welcome! You are client #{client_count}",
                    'data': [1, 2, 3, 4, 5],
                    'request_id': 1
                }
                time.sleep(0.1)  # 添加小延迟确保顺序
                queue.put(response)
                print(f"服务进程已发送请求1")
                
            elif msg['type'] == MessageType.DATA_RESPONSE:
                print(f"服务进程收到数据响应: {msg['processed_data']} (请求ID: {msg['request_id']})")
                
                if msg['request_id'] < 3:
                    new_data = [random.randint(10, 20) for _ in range(3)]
                    request = {
                        'type': MessageType.DATA_REQUEST,
                        'server_id': os.getpid(),
                        'message': "Process this data",
                        'data': new_data,
                        'request_id': msg['request_id'] + 1
                    }
                    time.sleep(0.1)
                    queue.put(request)
                    print(f"服务进程已发送请求{msg['request_id'] + 1}")
                else:
                    # 第三次响应后不发送新请求，等待客户端退出
                    pass
                    
            elif msg['type'] == MessageType.EXIT:
                print("服务进程收到退出信号，准备关闭...")
                break
                
        except Exception as e:
            print(f"服务进程异常: {e}")
            break

def client(queue, client_id):
    print(f"客户端 {client_id} 启动")
    
    greeting = {
        'type': MessageType.GREETING,
        'client_id': client_id,
        'timestamp': time.time()
    }
    queue.put(greeting)
    print("客户端已发送问候")
    
    request_count = 0
    
    while request_count < 3:  # 明确限制3次请求
        try:
            response = queue.get(timeout=5)
            
            if response['type'] == MessageType.DATA_REQUEST:
                request_count += 1
                current_request_id = response.get('request_id', request_count)
                print(f"客户端收到请求{current_request_id}: {response['message']}")
                
                processed_data = [x * 2 for x in response['data']]
                
                data_response = {
                    'type': MessageType.DATA_RESPONSE,
                    'client_id': client_id,
                    'processed_data': processed_data,
                    'original_data': response['data'],
                    'request_id': current_request_id
                }
                time.sleep(0.1)
                queue.put(data_response)
                print(f"客户端已发送响应{current_request_id}")
                
                # 只有完成3次请求后才退出
                if request_count >= 3:
                    time.sleep(0.2)  # 确保响应被服务端接收
                    exit_msg = {
                        'type': MessageType.EXIT,
                        'client_id': client_id,
                        'message': f"Client {client_id} completed all requests"
                    }
                    queue.put(exit_msg)
                    print(f"客户端 {client_id} 退出")
                    break
                    
        except Exception as e:
            print(f"客户端异常: {e}")
            break

if __name__ == "__main__":
    q = Queue()
    
    server_process = Process(target=server, args=(q,))
    server_process.start()
    
    time.sleep(1)
    
    client_process = Process(target=client, args=(q, 1001))
    client_process.start()
    
    client_process.join(timeout=15)
    server_process.terminate()
    server_process.join()
    
print("消息队列通信演示结束")