import os
import json
import time

def child_process(parent_to_child, child_to_parent):
    # 关闭不需要的端口
    os.close(parent_to_child[1])  # 关闭父到子的写端
    os.close(child_to_parent[0])  # 关闭子到父的读端
    
    # 接收父进程的问候
    data = os.read(parent_to_child[0], 1024)
    message = json.loads(data.decode())
    print(f"子进程收到: {message['content']} (时间: {message['timestamp']})")
    
    # 回复父进程
    reply = {
        "content": "Hello Parent! I'm your child process.",
        "timestamp": time.time(),
        "sender": "child"
    }
    os.write(child_to_parent[1], json.dumps(reply).encode())
    
    # 进行第二轮通信
    second_msg = os.read(parent_to_child[0], 1024)
    second_data = json.loads(second_msg.decode())
    print(f"子进程收到: {second_data['content']}")
    
    final_reply = {
        "content": "Goodbye Parent! Child process exiting.",
        "timestamp": time.time(),
        "status": "exit"
    }
    os.write(child_to_parent[1], json.dumps(final_reply).encode())
    
    # 关闭端口
    os.close(parent_to_child[0])
    os.close(child_to_parent[1])
    exit(0)

if __name__ == "__main__":
    # 创建两个管道：父到子 和 子到父
    parent_to_child = os.pipe()
    child_to_parent = os.pipe()
    
    pid = os.fork()
    
    if pid == 0:
        child_process(parent_to_child, child_to_parent)
    else:
        # 父进程：关闭不需要的端口
        os.close(parent_to_child[0])  # 关闭父到子的读端
        os.close(child_to_parent[1])  # 关闭子到父的写端
        
        # 发送第一条消息
        greeting = {
            "content": "Hello Child! I'm your parent process.",
            "timestamp": time.time(),
            "sender": "parent"
        }
        os.write(parent_to_child[1], json.dumps(greeting).encode())
        print("父进程已发送问候消息")
        
        # 等待子进程回复
        reply_data = os.read(child_to_parent[0], 1024)
        reply = json.loads(reply_data.decode())
        print(f"父进程收到: {reply['content']} (时间: {reply['timestamp']})")
        
        # 发送第二条消息
        second_msg = {
            "content": "How are you doing?",
            "timestamp": time.time(),
            "sender": "parent"
        }
        os.write(parent_to_child[1], json.dumps(second_msg).encode())
        print("父进程已发送第二条消息")
        
        # 等待最终回复
        final_data = os.read(child_to_parent[0], 1024)
        final_reply = json.loads(final_data.decode())
        print(f"父进程收到: {final_reply['content']} (状态: {final_reply['status']})")
        
        # 清理资源
        os.close(parent_to_child[1])
        os.close(child_to_parent[0])
        os.wait()
        print("父子进程通信结束")
