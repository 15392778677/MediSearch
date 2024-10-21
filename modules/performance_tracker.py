'''
Date: 2024-10-13 16:54:05
LastEditors: yangyehan 1958944515@qq.com
LastEditTime: 2024-10-18 16:55:17
FilePath: /MediSearch/modules/performance_tracker.py
Description: 
'''
# modules/performance_tracker.py
import sys
sys.path.append('..')
import time
import asyncio
from functools import wraps

# 存储函数性能数据的字典
func_performance = {}

# 全局变量用于存储程序总时间
program_start_time = None
program_end_time = None

def track_performance(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time

        # 更新性能数据
        if func.__name__ not in func_performance:
            func_performance[func.__name__] = {'calls': 0, 'total_time': 0}
        func_performance[func.__name__]['calls'] += 1
        func_performance[func.__name__]['total_time'] += elapsed_time

        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time

        # 更新性能数据
        if func.__name__ not in func_performance:
            func_performance[func.__name__] = {'calls': 0, 'total_time': 0}
        func_performance[func.__name__]['calls'] += 1
        func_performance[func.__name__]['total_time'] += elapsed_time

        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def start_program_timer():
    global program_start_time
    program_start_time = time.time()

def end_program_timer():
    global program_end_time
    program_end_time = time.time()

def print_performance_data():
    print("{:<40} {:<10} {:<20} {:<20}".format('函数名', '调用次数', '总时间(秒)', '平均时间(秒)'))
    print("-" * 115)
    for func, data in func_performance.items():
        avg_time = data['total_time'] / data['calls']
        print("{:<40} {:<10} {:<20.2f} {:<20.2f}".format(func, data['calls'], data['total_time'], avg_time))

    if program_start_time and program_end_time:
        total_time = program_end_time - program_start_time
        print("\n{:<40} {:<10.2f}".format('程序总时间(秒)', total_time))
    else:
        print("\n程序总时间数据不完整。")