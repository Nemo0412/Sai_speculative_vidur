"""
极端差异配置 - 创建更大的处理时间和容量差异
"""

import config

def create_extreme_config():
    """创建极端差异的配置"""
    print("=== 创建极端差异配置 ===")
    
    # 1. 大幅增加系统负载
    config.REQUEST_ARRIVAL_RATE = 15.0  # 提高15倍负载
    config.SIMULATION_TIME = 80.0
    
    # 2. 创建极端处理时间差异 (0.05 - 15.0)
    config.PREFILL_TIMES = [
        [0.05, 0.1, 15.0, 12.0],  # Draft 0: 0.05-15.0的极端差异
        [0.08, 0.15, 14.0, 11.0], # Draft 1
        [0.06, 0.12, 13.0, 10.0], # Draft 2
        [0.07, 0.13, 12.0, 9.5],  # Draft 3
        [0.09, 0.18, 11.0, 8.5],  # Draft 4
        [0.04, 0.08, 10.0, 7.5],  # Draft 5
        [0.1, 0.2, 9.0, 6.5],     # Draft 6
        [0.12, 0.25, 8.0, 5.5],   # Draft 7
        [0.15, 0.3, 7.0, 4.5],    # Draft 8
        [0.2, 0.4, 6.0, 3.5],     # Draft 9
        [0.25, 0.5, 5.0, 2.5],    # Draft 10
        [0.3, 0.6, 4.0, 1.5],     # Draft 11
        [0.4, 0.8, 3.0, 1.0],     # Draft 12
        [0.5, 1.0, 2.0, 0.8],     # Draft 13
        [0.6, 1.2, 1.5, 0.6],     # Draft 14
        [0.8, 1.5, 1.0, 0.4],     # Draft 15
        [1.0, 2.0, 0.8, 0.3],     # Draft 16
        [1.5, 3.0, 0.6, 0.2],     # Draft 17
        [2.0, 4.0, 0.4, 0.15],    # Draft 18
        [3.0, 6.0, 0.2, 0.1],     # Draft 19
    ]
    
    config.DECODE_TIMES = [
        [0.025, 0.05, 7.5, 6.0],  # Draft 0: 0.025-7.5的极端差异
        [0.04, 0.08, 7.0, 5.5],   # Draft 1
        [0.03, 0.06, 6.5, 5.0],   # Draft 2
        [0.035, 0.07, 6.0, 4.5],  # Draft 3
        [0.045, 0.09, 5.5, 4.0],  # Draft 4
        [0.02, 0.04, 5.0, 3.5],   # Draft 5
        [0.05, 0.1, 4.5, 3.0],    # Draft 6
        [0.06, 0.12, 4.0, 2.5],   # Draft 7
        [0.075, 0.15, 3.5, 2.0],  # Draft 8
        [0.1, 0.2, 3.0, 1.5],     # Draft 9
        [0.125, 0.25, 2.5, 1.0],  # Draft 10
        [0.15, 0.3, 2.0, 0.8],    # Draft 11
        [0.2, 0.4, 1.5, 0.6],     # Draft 12
        [0.25, 0.5, 1.0, 0.4],    # Draft 13
        [0.3, 0.6, 0.8, 0.3],     # Draft 14
        [0.4, 0.8, 0.6, 0.2],     # Draft 15
        [0.5, 1.0, 0.4, 0.15],    # Draft 16
        [0.75, 1.5, 0.3, 0.1],    # Draft 17
        [1.0, 2.0, 0.2, 0.08],    # Draft 18
        [1.5, 3.0, 0.1, 0.05],    # Draft 19
    ]
    
    # 3. 创建极端目标容量差异 (5 - 100)
    config.TARGET_CONFIGS = [
        {"queue_size": 5, "batch_size": 1},    # 很小 - 处理快速请求
        {"queue_size": 15, "batch_size": 3},   # 小 - 处理中等请求
        {"queue_size": 50, "batch_size": 10},  # 大 - 处理慢速请求
        {"queue_size": 100, "batch_size": 20}, # 很大 - 处理最慢请求
    ]
    
    # 4. 增加路由器队列大小以处理高负载
    config.ROUTER_QUEUE_SIZE = 200
    
    print(f"   请求到达率: {config.REQUEST_ARRIVAL_RATE} (提高15倍)")
    print(f"   仿真时间: {config.SIMULATION_TIME}")
    print(f"   路由器队列: {config.ROUTER_QUEUE_SIZE}")
    print(f"   处理时间范围: 0.025 - 15.0 (差异系数: 600)")
    print(f"   队列大小范围: 5 - 100 (差异系数: 20)")
    print(f"   批处理大小范围: 1 - 20 (差异系数: 20)")
    
    # 验证配置
    validate_extreme_config()

def validate_extreme_config():
    """验证极端配置"""
    print("\n=== 验证极端配置 ===")
    
    # 计算负载率
    total_batch_capacity = sum(t["batch_size"] for t in config.TARGET_CONFIGS)
    expected_requests = config.REQUEST_ARRIVAL_RATE * config.SIMULATION_TIME
    theoretical_max_throughput = total_batch_capacity * config.SIMULATION_TIME
    load_rate = expected_requests / theoretical_max_throughput
    
    print(f"   总批处理容量: {total_batch_capacity}")
    print(f"   预期请求数: {expected_requests}")
    print(f"   理论最大处理能力: {theoretical_max_throughput}")
    print(f"   系统负载率: {load_rate:.1%}")
    
    # 计算处理时间差异
    prefill_times = [t for row in config.PREFILL_TIMES for t in row]
    decode_times = [t for row in config.DECODE_TIMES for t in row]
    all_times = prefill_times + decode_times
    
    min_time = min(all_times)
    max_time = max(all_times)
    avg_time = sum(all_times) / len(all_times)
    time_variance = sum((t - avg_time)**2 for t in all_times) / len(all_times)
    
    print(f"   处理时间范围: {min_time:.3f} - {max_time:.1f}")
    print(f"   平均处理时间: {avg_time:.3f}")
    print(f"   时间方差: {time_variance:.4f}")
    print(f"   时间差异系数: {(max_time-min_time)/avg_time:.1f}")
    
    # 计算容量差异
    queue_sizes = [t["queue_size"] for t in config.TARGET_CONFIGS]
    batch_sizes = [t["batch_size"] for t in config.TARGET_CONFIGS]
    
    queue_min, queue_max = min(queue_sizes), max(queue_sizes)
    batch_min, batch_max = min(batch_sizes), max(batch_sizes)
    
    print(f"   队列大小范围: {queue_min} - {queue_max}")
    print(f"   批处理大小范围: {batch_min} - {batch_max}")
    print(f"   队列差异系数: {(queue_max-queue_min)/queue_min:.1f}")
    print(f"   批处理差异系数: {(batch_max-batch_min)/batch_min:.1f}")
    
    # 判断配置是否足够极端
    if load_rate > 0.8:
        print("   ✅ 系统负载足够高")
    else:
        print("   ❌ 系统负载仍然较低")
    
    if (max_time-min_time)/avg_time > 10:
        print("   ✅ 处理时间差异足够大")
    else:
        print("   ❌ 处理时间差异仍然较小")
    
    if (queue_max-queue_min)/queue_min > 10:
        print("   ✅ 容量差异足够大")
    else:
        print("   ❌ 容量差异仍然较小")

if __name__ == "__main__":
    create_extreme_config()
    print("\n✅ 极端差异配置创建完成！")
