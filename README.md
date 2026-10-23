# 操作系统实验

七次实验的程序和报告。实验一、二主要是 shell 脚本；实验三到七是 Python 对进程、同步、通信、死锁、分页和文件系统的模拟，其中一部分用 PyInstaller 打成了 Linux 可执行文件。

各次实验报告是对应目录下的 docx。

## 技术栈与关键词

- 技术栈：Python、Bash、bc、multiprocessing、threading、psutil、NumPy、Matplotlib、PyInstaller、Linux
- 关键词：操作系统、进程、信号量、读者写者、生产者消费者、管道、消息队列、信号通信、银行家算法、死锁检测、狒狒过河、页面置换、老化算法、TLB、目录比较、SHA-256

## 实验一、二

目录：`实验一二`

- `mycal.sh`：shell 计算器，读入表达式后用 `bc` 计算。
- 实验一报告对应进程观察和 shell 基础操作，没有单独的源码文件。

在 Git Bash、WSL 或 Linux 下运行：

```bash
bash mycal.sh
```

## 实验三：进程与同步

目录：`实验三四/python源代码/实验三`

| 文件 | 内容 |
| --- | --- |
| `process_ops.py` | 用 `multiprocessing` 创建子进程，查看 PID，并发送信号结束子进程。依赖 `psutil`。 |
| `writer_priority_rw.py` | 写者优先的读者-写者。用 `read_try` 挡住已有写者等待时新来的读者。 |
| `buggy_producer_consumer.py` | 故意不加锁的生产者-消费者，用来观察丢数据、重复消费等竞态。 |

## 实验四：进程通信

目录：`实验三四/python源代码/实验四`

| 文件 | 内容 |
| --- | --- |
| `pipe_communication.py` | 父子进程用一对匿名管道交换 JSON 消息。 |
| `message_queue.py` | 用 `multiprocessing.Queue` 模拟服务进程和多个客户进程。 |
| `signal_communication.py` | 父进程向子进程发送 `SIGUSR1`、`SIGUSR2`，子进程在处理函数里回应。 |

`实验三四/Linux可执行文件` 下是上述六个程序的打包结果，应在 Linux 上运行。

## 实验五：死锁

目录：`实验五六`

| 文件 | 内容 |
| --- | --- |
| `BankersAlgorithm.py` | 银行家算法。由 Max 和 Allocation 计算 Need，再找安全序列。 |
| `DeadlockDetection.py` | 用多组 Available、Max、Allocation 数据检测是否已经死锁。 |
| `BanboonCrossing.py` | 狒狒过绳。东、西两个方向互斥，同一方向可以同时通过，并避免双方同时抢绳造成的死锁。 |

直接运行对应的 `.py`。`实验五/banker_algorithm_result.txt` 是银行家算法的一次输出。

## 实验六：分页与 TLB

目录：`实验五六`

| 文件 | 内容 |
| --- | --- |
| `AgingPageReplacement.py` | 老化算法。每个页一个计数器，周期右移并在访问时置最高位，替换计数值最小的页。 |
| `measure_tlb_effect.py` | 改变数组大小和访问步长，测量内存访问时间，观察 TLB 失效的影响。 |

两个脚本都会用 Matplotlib 画图。`实验六/aging_simulation_results.txt` 是老化算法的一次统计结果。同目录下的 `AgingPageReplacement`、`TLBeffect` 等无后缀文件是 Linux 可执行文件。

## 实验七：目录比较

目录：`实验七`

`difftree.py` 递归比较两棵目录树，按相对路径对齐，用文件大小、修改时间和 SHA-256 判断新增、删除和内容变化。

```bash
python difftree.py 目录A 目录B
```

## 依赖

```bash
python -m pip install psutil numpy matplotlib
```

实验三的进程查看需要 `psutil`；实验六的计时和作图需要 `numpy` 与 `matplotlib`。信号和 `os.pipe` 相关的程序以 Linux 或 WSL 为准，Windows 上 `SIGUSR1` 一类信号不可用。
