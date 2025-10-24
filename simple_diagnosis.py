#!/usr/bin/env python3
"""
简单的性能诊断分析
"""

import config
import simulation
import time

def analyze_why_small_improvement():
    """分析为什么性能提升较小"""
    print("=== 性能提升较小的原因分析 ===")
    
    # 1. 系统负载分析
    print("\n1. 系统负载分析:")
    total_batch_capacity = sum(t["batch_size"] for t in config.TARGET_CONFIGS)
    expected_requests = config.REQUEST_ARRIVAL_RATE * config.SIMULATION_TIME
    theoretical_max_throughput = total_batch_capacity * config.SIMULATION_TIME
    
    print(f"   总批处理容量: {total_batch_capacity}")
    print(f"   请求到达率: {config.REQUEST_ARRIVAL_RATE}")
    print(f"   仿真时间: {config.SIMULATION_TIME}")
    print(f"   预期请求数: {expected_requests}")
    print(f"   理论最大处理能力: {theoretical_max_throughput}")
    print(f"   系统负载率: {expected_requests/theoretical_max_throughput:.2%}")
    
    if expected_requests/theoretical_max_throughput < 0.5:
        print("   ❌ 系统负载过低，算法差异不明显")
    else:
        print("   ✅ 系统负载适中")
    
    # 2. 处理时间差异分析
    print("\n2. 处理时间差异分析:")
    prefill_times = [t for row in config.PREFILL_TIMES for t in row]
    decode_times = [t for row in config.DECODE_TIMES for t in row]
    all_times = prefill_times + decode_times
    
    min_time = min(all_times)
    max_time = max(all_times)
    avg_time = sum(all_times) / len(all_times)
    time_variance = sum((t - avg_time)**2 for t in all_times) / len(all_times)
    
    print(f"   处理时间范围: {min_time:.2f} - {max_time:.2f}")
    print(f"   平均处理时间: {avg_time:.2f}")
    print(f"   时间方差: {time_variance:.4f}")
    print(f"   时间差异系数: {(max_time-min_time)/avg_time:.2f}")
    
    if (max_time-min_time)/avg_time < 0.5:
        print("   ❌ 处理时间差异太小，SJF算法效果有限")
    else:
        print("   ✅ 处理时间差异适中")
    
    # 3. 目标容量差异分析
    print("\n3. 目标容量差异分析:")
    queue_sizes = [t["queue_size"] for t in config.TARGET_CONFIGS]
    batch_sizes = [t["batch_size"] for t in config.TARGET_CONFIGS]
    
    queue_min, queue_max = min(queue_sizes), max(queue_sizes)
    batch_min, batch_max = min(batch_sizes), max(batch_sizes)
    
    print(f"   队列大小范围: {queue_min} - {queue_max}")
    print(f"   批处理大小范围: {batch_min} - {batch_max}")
    print(f"   队列差异系数: {(queue_max-queue_min)/queue_min:.2f}")
    print(f"   批处理差异系数: {(batch_max-batch_min)/batch_min:.2f}")
    
    if (queue_max-queue_min)/queue_min < 0.5:
        print("   ❌ 目标容量差异太小，负载均衡效果有限")
    else:
        print("   ✅ 目标容量差异适中")
    
    # 4. 算法配置问题
    print("\n4. 算法配置问题:")
    print(f"   当前路由算法: {config.ROUTING_ALGORITHM}")
    print(f"   当前调度算法: {config.SCHEDULING_ALGORITHM}")
    
    # 检查配置是否正确应用
    if config.ROUTING_ALGORITHM == 'shortest_queue':
        print("   ❌ 配置没有正确应用！应该使用round_robin和least_loaded")
    
    return {
        'load_rate': expected_requests/theoretical_max_throughput,
        'time_variance': time_variance,
        'queue_variance': (queue_max-queue_min)/queue_min,
        'batch_variance': (batch_max-batch_min)/batch_min
    }

def test_with_higher_load():
    """测试更高负载下的性能差异"""
    print("\n=== 高负载测试 ===")
    
    # 备份原始配置
    original_arrival_rate = config.REQUEST_ARRIVAL_RATE
    original_simulation_time = config.SIMULATION_TIME
    
    try:
        # 设置高负载配置
        config.REQUEST_ARRIVAL_RATE = 2.0  # 提高2倍
        config.SIMULATION_TIME = 100.0     # 减少时间但保持高负载
        
        print(f"   高负载配置: 到达率={config.REQUEST_ARRIVAL_RATE}, 时间={config.SIMULATION_TIME}")
        
        # 测试vanilla
        config.ROUTING_ALGORITHM = 'round_robin'
        config.SCHEDULING_ALGORITHM = 'fifo'
        
        sim = simulation.SchedulingSimulation()
        result_vanilla = sim.run_simulation(simulation_time=50.0)
        
        # 测试优化
        config.ROUTING_ALGORITHM = 'least_loaded'
        config.SCHEDULING_ALGORITHM = 'priority'
        
        sim = simulation.SchedulingSimulation()
        result_optimized = sim.run_simulation(simulation_time=50.0)
        
        # 计算改进
        completion_improvement = (result_optimized.completion_rate - result_vanilla.completion_rate) / result_vanilla.completion_rate * 100
        response_improvement = (result_vanilla.average_response_time - result_optimized.average_response_time) / result_vanilla.average_response_time * 100
        throughput_improvement = (result_optimized.throughput - result_vanilla.throughput) / result_vanilla.throughput * 100
        
        print(f"   Vanilla: 完成率={result_vanilla.completion_rate:.2%}, 响应时间={result_vanilla.average_response_time:.4f}")
        print(f"   优化: 完成率={result_optimized.completion_rate:.2%}, 响应时间={result_optimized.average_response_time:.4f}")
        print(f"   改进: 完成率={completion_improvement:+.2f}%, 响应时间={response_improvement:+.2f}%, 吞吐量={throughput_improvement:+.2f}%")
        
        if completion_improvement > 5:
            print("   ✅ 高负载下算法差异明显")
        else:
            print("   ❌ 即使高负载下算法差异仍然较小")
            
    finally:
        # 恢复原始配置
        config.REQUEST_ARRIVAL_RATE = original_arrival_rate
        config.SIMULATION_TIME = original_simulation_time

def test_with_extreme_differences():
    """测试极端差异下的性能"""
    print("\n=== 极端差异测试 ===")
    
    # 备份原始配置
    original_prefill = config.PREFILL_TIMES
    original_decode = config.DECODE_TIMES
    original_target_configs = config.TARGET_CONFIGS
    
    try:
        # 创建极端差异的配置
        # 处理时间差异：0.1 到 5.0
        config.PREFILL_TIMES = [
            [0.1, 0.2, 5.0, 4.8] for _ in range(20)
        ]
        config.DECODE_TIMES = [
            [0.05, 0.1, 2.5, 2.4] for _ in range(20)
        ]
        
        # 目标容量差异：5 到 50
        config.TARGET_CONFIGS = [
            {"queue_size": 5, "batch_size": 1},   # 很小
            {"queue_size": 10, "batch_size": 2},  # 小
            {"queue_size": 30, "batch_size": 8},  # 大
            {"queue_size": 50, "batch_size": 10}, # 很大
        ]
        
        print("   极端差异配置:")
        print(f"   处理时间范围: 0.05 - 5.0")
        print(f"   队列大小范围: 5 - 50")
        print(f"   批处理大小范围: 1 - 10")
        
        # 测试vanilla
        config.ROUTING_ALGORITHM = 'round_robin'
        config.SCHEDULING_ALGORITHM = 'fifo'
        
        sim = simulation.SchedulingSimulation()
        result_vanilla = sim.run_simulation(simulation_time=30.0)
        
        # 测试优化
        config.ROUTING_ALGORITHM = 'least_loaded'
        config.SCHEDULING_ALGORITHM = 'shortest_job_first'
        
        sim = simulation.SchedulingSimulation()
        result_optimized = sim.run_simulation(simulation_time=30.0)
        
        # 计算改进
        completion_improvement = (result_optimized.completion_rate - result_vanilla.completion_rate) / result_vanilla.completion_rate * 100
        response_improvement = (result_vanilla.average_response_time - result_optimized.average_response_time) / result_vanilla.average_response_time * 100
        throughput_improvement = (result_optimized.throughput - result_vanilla.throughput) / result_vanilla.throughput * 100
        
        print(f"   Vanilla: 完成率={result_vanilla.completion_rate:.2%}, 响应时间={result_vanilla.average_response_time:.4f}")
        print(f"   优化: 完成率={result_optimized.completion_rate:.2%}, 响应时间={result_optimized.average_response_time:.4f}")
        print(f"   改进: 完成率={completion_improvement:+.2f}%, 响应时间={response_improvement:+.2f}%, 吞吐量={throughput_improvement:+.2f}%")
        
        if completion_improvement > 10:
            print("   ✅ 极端差异下算法效果显著")
        else:
            print("   ❌ 即使极端差异下算法效果仍然有限")
            
    finally:
        # 恢复原始配置
        config.PREFILL_TIMES = original_prefill
        config.DECODE_TIMES = original_decode
        config.TARGET_CONFIGS = original_target_configs

def main():
    print("性能提升较小的原因诊断")
    print("=" * 50)
    
    # 分析当前配置
    metrics = analyze_why_small_improvement()
    
    # 测试高负载
    test_with_higher_load()
    
    # 测试极端差异
    test_with_extreme_differences()
    
    print("\n=== 诊断结论 ===")
    print("性能提升较小的主要原因:")
    print("1. 系统负载率过低 ({:.1%})，算法差异不明显".format(metrics['load_rate']))
    print("2. 处理时间差异较小 (方差: {:.4f})，SJF效果有限".format(metrics['time_variance']))
    print("3. 目标容量差异较小 (队列差异: {:.1%})，负载均衡效果有限".format(metrics['queue_variance']))
    print("4. 批处理机制可能掩盖了调度算法的差异")
    print("5. 请求到达模式相对均匀，轮询和负载最轻差异不大")
    
    print("\n建议改进方案:")
    print("1. 增加系统负载 (提高请求到达率到2.0-3.0)")
    print("2. 增加处理时间差异 (范围扩大到0.1-10.0)")
    print("3. 增加目标容量差异 (队列大小范围扩大到5-50)")
    print("4. 减少批处理大小，让调度算法差异更明显")
    print("5. 使用更复杂的请求到达模式")

if __name__ == "__main__":
    main()
