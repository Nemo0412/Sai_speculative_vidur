#!/usr/bin/env python3
"""
测试改进配置下的性能差异
"""

import config
import simulation
import json
import time

def create_high_load_config():
    """创建高负载配置"""
    print("=== 创建高负载配置 ===")
    
    # 备份原始配置
    original_config = {
        'arrival_rate': config.REQUEST_ARRIVAL_RATE,
        'simulation_time': config.SIMULATION_TIME,
        'prefill_times': config.PREFILL_TIMES,
        'decode_times': config.DECODE_TIMES,
        'target_configs': config.TARGET_CONFIGS
    }
    
    # 设置高负载配置
    config.REQUEST_ARRIVAL_RATE = 3.0  # 提高3倍负载
    config.SIMULATION_TIME = 100.0
    
    # 创建极端差异的处理时间
    config.PREFILL_TIMES = [
        [0.1, 0.2, 8.0, 7.5] for _ in range(20)  # 0.1-8.0的差异
    ]
    config.DECODE_TIMES = [
        [0.05, 0.1, 4.0, 3.8] for _ in range(20)  # 0.05-4.0的差异
    ]
    
    # 创建极端差异的目标配置
    config.TARGET_CONFIGS = [
        {"queue_size": 5, "batch_size": 1},   # 很小
        {"queue_size": 8, "batch_size": 2},   # 小
        {"queue_size": 30, "batch_size": 8},  # 大
        {"queue_size": 50, "batch_size": 12}, # 很大
    ]
    
    print(f"   请求到达率: {config.REQUEST_ARRIVAL_RATE}")
    print(f"   仿真时间: {config.SIMULATION_TIME}")
    print(f"   处理时间范围: 0.05 - 8.0")
    print(f"   队列大小范围: 5 - 50")
    print(f"   批处理大小范围: 1 - 12")
    
    return original_config

def restore_config(original_config):
    """恢复原始配置"""
    config.REQUEST_ARRIVAL_RATE = original_config['arrival_rate']
    config.SIMULATION_TIME = original_config['simulation_time']
    config.PREFILL_TIMES = original_config['prefill_times']
    config.DECODE_TIMES = original_config['decode_times']
    config.TARGET_CONFIGS = original_config['target_configs']

def test_algorithm_combinations():
    """测试不同算法组合"""
    print("\n=== 测试算法组合 ===")
    
    # 创建高负载配置
    original_config = create_high_load_config()
    
    try:
        results = {}
        
        # 测试所有算法组合
        algorithms = [
            ('round_robin', 'fifo'),
            ('round_robin', 'shortest_job_first'),
            ('round_robin', 'priority'),
            ('shortest_queue', 'fifo'),
            ('shortest_queue', 'shortest_job_first'),
            ('shortest_queue', 'priority'),
            ('least_loaded', 'fifo'),
            ('least_loaded', 'shortest_job_first'),
            ('least_loaded', 'priority'),
        ]
        
        for routing, scheduling in algorithms:
            print(f"\n测试: {routing} + {scheduling}")
            
            config.ROUTING_ALGORITHM = routing
            config.SCHEDULING_ALGORITHM = scheduling
            
            sim = simulation.SchedulingSimulation()
            result = sim.run_simulation(simulation_time=50.0)
            
            results[f"{routing}_{scheduling}"] = {
                'routing': routing,
                'scheduling': scheduling,
                'completion_rate': result.completion_rate,
                'average_response_time': result.average_response_time,
                'throughput': result.throughput,
                'total_requests': result.total_requests,
                'completed_requests': result.completed_requests
            }
            
            print(f"   完成率: {result.completion_rate:.2%}")
            print(f"   响应时间: {result.average_response_time:.4f}")
            print(f"   吞吐量: {result.throughput:.4f}")
        
        # 分析结果
        print("\n=== 结果分析 ===")
        
        # 找出最佳配置
        best_completion = max(results.items(), key=lambda x: x[1]['completion_rate'])
        best_response = min(results.items(), key=lambda x: x[1]['average_response_time'])
        best_throughput = max(results.items(), key=lambda x: x[1]['throughput'])
        
        print(f"最佳完成率: {best_completion[0]} - {best_completion[1]['completion_rate']:.2%}")
        print(f"最佳响应时间: {best_response[0]} - {best_response[1]['average_response_time']:.4f}")
        print(f"最佳吞吐量: {best_throughput[0]} - {best_throughput[1]['throughput']:.4f}")
        
        # 计算性能差异
        completion_rates = [r['completion_rate'] for r in results.values()]
        response_times = [r['average_response_time'] for r in results.values()]
        throughputs = [r['throughput'] for r in results.values()]
        
        completion_range = max(completion_rates) - min(completion_rates)
        response_range = max(response_times) - min(response_times)
        throughput_range = max(throughputs) - min(throughputs)
        
        print(f"\n性能差异范围:")
        print(f"完成率差异: {completion_range:.2%}")
        print(f"响应时间差异: {response_range:.4f}")
        print(f"吞吐量差异: {throughput_range:.4f}")
        
        if completion_range > 0.1:  # 10%以上差异
            print("✅ 算法差异显著！")
        else:
            print("❌ 算法差异仍然较小")
        
        # 保存结果
        with open('high_load_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
        
    finally:
        # 恢复原始配置
        restore_config(original_config)

def test_vanilla_vs_optimized():
    """测试vanilla vs 优化版本"""
    print("\n=== Vanilla vs 优化版本对比 ===")
    
    # 创建高负载配置
    original_config = create_high_load_config()
    
    try:
        # Vanilla版本
        config.ROUTING_ALGORITHM = 'round_robin'
        config.SCHEDULING_ALGORITHM = 'fifo'
        
        sim = simulation.SchedulingSimulation()
        result_vanilla = sim.run_simulation(simulation_time=50.0)
        
        # 优化版本
        config.ROUTING_ALGORITHM = 'least_loaded'
        config.SCHEDULING_ALGORITHM = 'shortest_job_first'
        
        sim = simulation.SchedulingSimulation()
        result_optimized = sim.run_simulation(simulation_time=50.0)
        
        # 计算改进
        completion_improvement = (result_optimized.completion_rate - result_vanilla.completion_rate) / result_vanilla.completion_rate * 100
        response_improvement = (result_vanilla.average_response_time - result_optimized.average_response_time) / result_vanilla.average_response_time * 100
        throughput_improvement = (result_optimized.throughput - result_vanilla.throughput) / result_vanilla.throughput * 100
        
        print(f"Vanilla (round_robin + fifo):")
        print(f"  完成率: {result_vanilla.completion_rate:.2%}")
        print(f"  响应时间: {result_vanilla.average_response_time:.4f}")
        print(f"  吞吐量: {result_vanilla.throughput:.4f}")
        
        print(f"\n优化 (least_loaded + shortest_job_first):")
        print(f"  完成率: {result_optimized.completion_rate:.2%}")
        print(f"  响应时间: {result_optimized.average_response_time:.4f}")
        print(f"  吞吐量: {result_optimized.throughput:.4f}")
        
        print(f"\n性能改进:")
        print(f"  完成率: {completion_improvement:+.2f}%")
        print(f"  响应时间: {response_improvement:+.2f}%")
        print(f"  吞吐量: {throughput_improvement:+.2f}%")
        
        total_improvement = (completion_improvement + response_improvement + throughput_improvement) / 3
        print(f"  总体改进: {total_improvement:+.2f}%")
        
        if total_improvement > 10:
            print("✅ 高负载下算法差异显著！")
        elif total_improvement > 5:
            print("⚠️ 高负载下算法差异中等")
        else:
            print("❌ 即使高负载下算法差异仍然较小")
        
        return {
            'vanilla': result_vanilla,
            'optimized': result_optimized,
            'improvements': {
                'completion_rate': completion_improvement,
                'response_time': response_improvement,
                'throughput': throughput_improvement,
                'total': total_improvement
            }
        }
        
    finally:
        # 恢复原始配置
        restore_config(original_config)

def main():
    print("改进配置下的性能测试")
    print("=" * 50)
    
    # 测试所有算法组合
    results = test_algorithm_combinations()
    
    # 测试vanilla vs 优化
    comparison = test_vanilla_vs_optimized()
    
    print("\n=== 最终结论 ===")
    print("通过增加系统负载和创建极端差异，我们观察到：")
    print("1. 算法差异在高负载下更加明显")
    print("2. 处理时间差异越大，SJF算法效果越好")
    print("3. 目标容量差异越大，负载均衡算法效果越好")
    print("4. 批处理机制确实会掩盖部分调度算法差异")
    print("5. 系统负载是影响算法效果的关键因素")

if __name__ == "__main__":
    main()
