#!/usr/bin/env python3
"""
性能诊断脚本 - 分析为什么性能提升较小
"""

import sys
import json
import time
from collections import defaultdict
import config
import simulation
from models import Request, RequestType

def analyze_system_bottlenecks():
    """分析系统瓶颈"""
    print("=== 系统瓶颈分析 ===")
    
    # 1. 队列利用率分析
    print("\n1. 队列利用率分析:")
    total_queue_capacity = config.ROUTER_QUEUE_SIZE + sum(t["queue_size"] for t in config.TARGET_CONFIGS)
    print(f"   总队列容量: {total_queue_capacity}")
    print(f"   路由器队列: {config.ROUTER_QUEUE_SIZE} ({config.ROUTER_QUEUE_SIZE/total_queue_capacity:.1%})")
    for i, target in enumerate(config.TARGET_CONFIGS):
        print(f"   Target {i}: {target['queue_size']} ({target['queue_size']/total_queue_capacity:.1%})")
    
    # 2. 处理能力分析
    print("\n2. 处理能力分析:")
    total_batch_capacity = sum(t["batch_size"] for t in config.TARGET_CONFIGS)
    print(f"   总批处理容量: {total_batch_capacity}")
    print(f"   请求到达率: {config.REQUEST_ARRIVAL_RATE} 请求/时间单位")
    print(f"   理论最大处理率: {total_batch_capacity} 请求/时间单位")
    
    # 3. 处理时间分析
    print("\n3. 处理时间分析:")
    prefill_times = [t for row in config.PREFILL_TIMES for t in row]
    decode_times = [t for row in config.DECODE_TIMES for t in row]
    all_times = prefill_times + decode_times
    
    print(f"   处理时间范围: {min(all_times):.2f} - {max(all_times):.2f}")
    print(f"   平均处理时间: {sum(all_times)/len(all_times):.2f}")
    print(f"   处理时间方差: {sum((t - sum(all_times)/len(all_times))**2 for t in all_times)/len(all_times):.4f}")
    
    # 4. 系统负载分析
    print("\n4. 系统负载分析:")
    expected_requests = config.REQUEST_ARRIVAL_RATE * config.SIMULATION_TIME
    print(f"   预期请求数: {expected_requests:.0f}")
    print(f"   系统是否过载: {'是' if expected_requests > total_batch_capacity * config.SIMULATION_TIME else '否'}")

def run_detailed_simulation_analysis():
    """运行详细的仿真分析"""
    print("\n=== 详细仿真分析 ===")
    
    # 运行vanilla配置
    print("\n1. Vanilla配置详细分析:")
    config.ROUTING_ALGORITHM = 'round_robin'
    config.SCHEDULING_ALGORITHM = 'fifo'
    
    sim = simulation.SchedulingSimulation()
    
    # 收集详细统计信息
    class DetailedAnalyzer:
        def __init__(self):
            self.router_queue_utilization = []
            self.target_queue_utilizations = [[] for _ in range(4)]
            self.batch_processing_times = []
            self.request_waiting_times = []
            self.routing_decisions = defaultdict(int)
            self.scheduling_decisions = defaultdict(int)
        
        def analyze_step(self, sim, current_time):
            # 路由器队列利用率
            router_util = len(sim.router.queue) / sim.router.queue_size
            self.router_queue_utilization.append(router_util)
            
            # 目标队列利用率
            for i, target in enumerate(sim.target_models):
                target_util = len(target.queue) / target.queue_size
                self.target_queue_utilizations[i].append(target_util)
            
            # 批处理时间
            for target in sim.target_models:
                if target.is_batch_ready():
                    batch_time = max(req.processing_time for req in target.current_batch)
                    self.batch_processing_times.append(batch_time)
    
    analyzer = DetailedAnalyzer()
    
    # 修改仿真以收集数据
    original_process = sim._finish_remaining_requests
    def process_with_analysis():
        # 在每次时间步收集数据
        for i in range(0, int(config.SIMULATION_TIME * 10)):  # 每0.1时间单位收集一次
            current_time = i * 0.1
            analyzer.analyze_step(sim, current_time)
        return original_process()
    
    sim._finish_remaining_requests = process_with_analysis
    result_vanilla = sim.run_simulation(simulation_time=50.0)
    
    print(f"   Vanilla结果: 完成率={result_vanilla.completion_rate:.2%}, 响应时间={result_vanilla.average_response_time:.4f}")
    
    # 分析vanilla配置的瓶颈
    avg_router_util = sum(analyzer.router_queue_utilization) / len(analyzer.router_queue_utilization)
    avg_target_utils = [sum(utils) / len(utils) for utils in analyzer.target_queue_utilizations]
    
    print(f"   平均路由器队列利用率: {avg_router_util:.2%}")
    for i, util in enumerate(avg_target_utils):
        print(f"   平均Target {i}队列利用率: {util:.2%}")
    
    if analyzer.batch_processing_times:
        avg_batch_time = sum(analyzer.batch_processing_times) / len(analyzer.batch_processing_times)
        print(f"   平均批处理时间: {avg_batch_time:.4f}")
    
    # 运行优化配置
    print("\n2. 优化配置详细分析:")
    config.ROUTING_ALGORITHM = 'least_loaded'
    config.SCHEDULING_ALGORITHM = 'priority'
    
    sim = simulation.SchedulingSimulation()
    analyzer_opt = DetailedAnalyzer()
    sim._finish_remaining_requests = process_with_analysis
    result_optimized = sim.run_simulation(simulation_time=50.0)
    
    print(f"   优化结果: 完成率={result_optimized.completion_rate:.2%}, 响应时间={result_optimized.average_response_time:.4f}")
    
    # 分析优化配置的瓶颈
    avg_router_util_opt = sum(analyzer_opt.router_queue_utilization) / len(analyzer_opt.router_queue_utilization)
    avg_target_utils_opt = [sum(utils) / len(utils) for utils in analyzer_opt.target_queue_utilizations]
    
    print(f"   平均路由器队列利用率: {avg_router_util_opt:.2%}")
    for i, util in enumerate(avg_target_utils_opt):
        print(f"   平均Target {i}队列利用率: {util:.2%}")
    
    if analyzer_opt.batch_processing_times:
        avg_batch_time_opt = sum(analyzer_opt.batch_processing_times) / len(analyzer_opt.batch_processing_times)
        print(f"   平均批处理时间: {avg_batch_time_opt:.4f}")
    
    return analyzer, analyzer_opt, result_vanilla, result_optimized

def analyze_algorithm_effectiveness():
    """分析算法有效性"""
    print("\n=== 算法有效性分析 ===")
    
    # 1. 处理时间差异分析
    print("\n1. 处理时间差异分析:")
    prefill_times = [t for row in config.PREFILL_TIMES for t in row]
    decode_times = [t for row in config.DECODE_TIMES for t in row]
    
    prefill_variance = sum((t - sum(prefill_times)/len(prefill_times))**2 for t in prefill_times) / len(prefill_times)
    decode_variance = sum((t - sum(decode_times)/len(decode_times))**2 for t in decode_times) / len(decode_times)
    
    print(f"   Prefill时间方差: {prefill_variance:.4f}")
    print(f"   Decode时间方差: {decode_variance:.4f}")
    print(f"   时间差异是否显著: {'是' if prefill_variance > 0.1 or decode_variance > 0.1 else '否'}")
    
    # 2. 目标容量差异分析
    print("\n2. 目标容量差异分析:")
    queue_sizes = [t["queue_size"] for t in config.TARGET_CONFIGS]
    batch_sizes = [t["batch_size"] for t in config.TARGET_CONFIGS]
    
    queue_variance = sum((s - sum(queue_sizes)/len(queue_sizes))**2 for s in queue_sizes) / len(queue_sizes)
    batch_variance = sum((s - sum(batch_sizes)/len(batch_sizes))**2 for s in batch_sizes) / len(batch_sizes)
    
    print(f"   队列大小方差: {queue_variance:.2f}")
    print(f"   批处理大小方差: {batch_variance:.2f}")
    print(f"   容量差异是否显著: {'是' if queue_variance > 10 or batch_variance > 2 else '否'}")
    
    # 3. 负载不均衡程度
    print("\n3. 负载不均衡程度分析:")
    max_queue = max(queue_sizes)
    min_queue = min(queue_sizes)
    imbalance_ratio = max_queue / min_queue
    print(f"   最大/最小队列比例: {imbalance_ratio:.2f}")
    print(f"   负载不均衡程度: {'高' if imbalance_ratio > 2 else '中等' if imbalance_ratio > 1.5 else '低'}")

def suggest_improvements():
    """建议改进方案"""
    print("\n=== 改进建议 ===")
    
    print("\n1. 增加系统负载:")
    print("   - 提高请求到达率 (当前: 1.0)")
    print("   - 增加仿真时间 (当前: 150.0)")
    print("   - 减少目标模型数量 (当前: 4)")
    
    print("\n2. 增加处理时间差异:")
    print("   - 增加不同draft-target组合的处理时间差异")
    print("   - 创建更极端的处理时间分布")
    
    print("\n3. 增加目标容量差异:")
    print("   - 增加不同目标的队列大小差异")
    print("   - 增加不同目标的批处理大小差异")
    
    print("\n4. 优化算法参数:")
    print("   - 调整路由器队列大小")
    print("   - 优化目标模型配置")
    print("   - 调整请求到达模式")

def main():
    print("性能诊断分析")
    print("=" * 50)
    
    # 分析系统瓶颈
    analyze_system_bottlenecks()
    
    # 运行详细仿真分析
    analyzer_vanilla, analyzer_opt, result_vanilla, result_optimized = run_detailed_simulation_analysis()
    
    # 分析算法有效性
    analyze_algorithm_effectiveness()
    
    # 建议改进方案
    suggest_improvements()
    
    print("\n=== 诊断结论 ===")
    print("性能提升较小的可能原因:")
    print("1. 系统负载相对较低，算法差异不明显")
    print("2. 处理时间差异不够大，SJF效果有限")
    print("3. 目标容量差异不够大，负载均衡效果有限")
    print("4. 请求到达模式相对均匀，轮询和负载最轻差异不大")
    print("5. 批处理机制可能掩盖了调度算法的差异")

if __name__ == "__main__":
    main()
