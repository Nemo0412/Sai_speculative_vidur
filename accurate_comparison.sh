#!/bin/bash

# 准确的性能比较脚本
echo "=========================================="
echo "准确的调度算法性能比较分析"
echo "=========================================="

# 创建结果目录
mkdir -p results
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="results/accurate_comparison_${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo "结果将保存到: $RESULTS_DIR"
echo ""

# 1. Vanilla版本测试 (round_robin + fifo)
echo "1. 测试Vanilla版本 (round_robin + fifo)..."
echo "----------------------------------------"

python3 -c "
import sys
sys.path.append('.')
import config
import simulation
import json
import time

# 备份原始配置
original_routing = config.ROUTING_ALGORITHM
original_scheduling = config.SCHEDULING_ALGORITHM

try:
    # 设置vanilla配置
    config.ROUTING_ALGORITHM = 'round_robin'
    config.SCHEDULING_ALGORITHM = 'fifo'
    
    start_time = time.time()
    sim = simulation.SchedulingSimulation()
    result = sim.run_simulation(simulation_time=100.0)
    vanilla_time = time.time() - start_time
    
    print(f'Vanilla版本结果 (round_robin + fifo):')
    print(f'  总请求数: {result.total_requests}')
    print(f'  完成请求数: {result.completed_requests}')
    print(f'  完成率: {result.completion_rate:.2%}')
    print(f'  平均响应时间: {result.average_response_time:.4f}')
    print(f'  吞吐量: {result.throughput:.4f}')
    print(f'  仿真运行时间: {vanilla_time:.4f}秒')
    
    # 保存结果
    vanilla_results = {
        'version': 'vanilla',
        'routing_algorithm': 'round_robin',
        'scheduling_algorithm': 'fifo',
        'total_requests': result.total_requests,
        'completed_requests': result.completed_requests,
        'completion_rate': result.completion_rate,
        'average_response_time': result.average_response_time,
        'throughput': result.throughput,
        'simulation_time': vanilla_time
    }
    
    with open('$RESULTS_DIR/vanilla_results.json', 'w') as f:
        json.dump(vanilla_results, f, indent=2)
        
finally:
    # 恢复原始配置
    config.ROUTING_ALGORITHM = original_routing
    config.SCHEDULING_ALGORITHM = original_scheduling
"

echo ""

# 2. 优化版本测试 (least_loaded + priority)
echo "2. 测试优化版本 (least_loaded + priority)..."
echo "----------------------------------------"

python3 -c "
import sys
sys.path.append('.')
import config
import simulation
import json
import time

# 备份原始配置
original_routing = config.ROUTING_ALGORITHM
original_scheduling = config.SCHEDULING_ALGORITHM

try:
    # 设置优化配置
    config.ROUTING_ALGORITHM = 'least_loaded'
    config.SCHEDULING_ALGORITHM = 'priority'
    
    start_time = time.time()
    sim = simulation.SchedulingSimulation()
    result = sim.run_simulation(simulation_time=100.0)
    optimized_time = time.time() - start_time
    
    print(f'优化版本结果 (least_loaded + priority):')
    print(f'  总请求数: {result.total_requests}')
    print(f'  完成请求数: {result.completed_requests}')
    print(f'  完成率: {result.completion_rate:.2%}')
    print(f'  平均响应时间: {result.average_response_time:.4f}')
    print(f'  吞吐量: {result.throughput:.4f}')
    print(f'  仿真运行时间: {optimized_time:.4f}秒')
    
    # 保存结果
    optimized_results = {
        'version': 'optimized',
        'routing_algorithm': 'least_loaded',
        'scheduling_algorithm': 'priority',
        'total_requests': result.total_requests,
        'completed_requests': result.completed_requests,
        'completion_rate': result.completion_rate,
        'average_response_time': result.average_response_time,
        'throughput': result.throughput,
        'simulation_time': optimized_time
    }
    
    with open('$RESULTS_DIR/optimized_results.json', 'w') as f:
        json.dump(optimized_results, f, indent=2)
        
finally:
    # 恢复原始配置
    config.ROUTING_ALGORITHM = original_routing
    config.SCHEDULING_ALGORITHM = original_scheduling
"

echo ""

# 3. 详细分配分析
echo "3. 详细分析Draft和Target分配模式..."
echo "----------------------------------------"

python3 -c "
import sys
sys.path.append('.')
import config
import simulation
import json
from collections import defaultdict

# 创建分配分析器
class DetailedAllocationAnalyzer:
    def __init__(self):
        self.draft_assignments = defaultdict(list)  # draft_id -> [target_ids]
        self.target_assignments = defaultdict(list)  # target_id -> [draft_ids]
        self.request_assignments = []  # [(draft_id, target_id, request_type)]
        self.target_loads = defaultdict(int)
        self.draft_loads = defaultdict(int)
    
    def analyze_request(self, request):
        if request.target_model_id is not None:
            self.draft_assignments[request.draft_model_id].append(request.target_model_id)
            self.target_assignments[request.target_model_id].append(request.draft_model_id)
            self.request_assignments.append((request.draft_model_id, request.target_model_id, request.request_type.value))
            self.target_loads[request.target_model_id] += 1
            self.draft_loads[request.draft_model_id] += 1

# 运行vanilla配置分析
print('Vanilla配置 (round_robin + fifo) 分配分析:')
config.ROUTING_ALGORITHM = 'round_robin'
config.SCHEDULING_ALGORITHM = 'fifo'

sim = simulation.SchedulingSimulation()
analyzer_vanilla = DetailedAllocationAnalyzer()

# 修改simulation以收集分配数据
original_process = sim._finish_remaining_requests
def process_with_analysis(analyzer):
    def wrapper():
        # 收集所有请求的分配信息
        for request in sim.router.queue:
            analyzer.analyze_request(request)
        for target in sim.target_models:
            for request in target.queue:
                analyzer.analyze_request(request)
            for request in target.current_batch:
                analyzer.analyze_request(request)
        for request in sim.completed_requests:
            analyzer.analyze_request(request)
        return original_process()
    return wrapper

sim._finish_remaining_requests = process_with_analysis(analyzer_vanilla)
result_vanilla = sim.run_simulation(simulation_time=50.0)

print('Draft到Target分配 (前10个draft):')
for draft_id in range(10):
    targets = analyzer_vanilla.draft_assignments[draft_id]
    if targets:
        target_counts = {i: targets.count(i) for i in range(4)}
        print(f'  Draft {draft_id:2d}: {dict(target_counts)}')

print('Target负载分布:')
for target_id in range(4):
    load = analyzer_vanilla.target_loads[target_id]
    print(f'  Target {target_id}: {load} 个请求')

# 运行优化配置分析
print('')
print('优化配置 (least_loaded + priority) 分配分析:')
config.ROUTING_ALGORITHM = 'least_loaded'
config.SCHEDULING_ALGORITHM = 'priority'

sim = simulation.SchedulingSimulation()
analyzer_optimized = DetailedAllocationAnalyzer()
sim._finish_remaining_requests = process_with_analysis(analyzer_optimized)
result_optimized = sim.run_simulation(simulation_time=50.0)

print('Draft到Target分配 (前10个draft):')
for draft_id in range(10):
    targets = analyzer_optimized.draft_assignments[draft_id]
    if targets:
        target_counts = {i: targets.count(i) for i in range(4)}
        print(f'  Draft {draft_id:2d}: {dict(target_counts)}')

print('Target负载分布:')
for target_id in range(4):
    load = analyzer_optimized.target_loads[target_id]
    print(f'  Target {target_id}: {load} 个请求')

# 保存详细分配分析
allocation_analysis = {
    'vanilla': {
        'draft_assignments': dict(analyzer_vanilla.draft_assignments),
        'target_loads': dict(analyzer_vanilla.target_loads),
        'request_assignments': analyzer_vanilla.request_assignments
    },
    'optimized': {
        'draft_assignments': dict(analyzer_optimized.draft_assignments),
        'target_loads': dict(analyzer_optimized.target_loads),
        'request_assignments': analyzer_optimized.request_assignments
    }
}

with open('$RESULTS_DIR/detailed_allocation_analysis.json', 'w') as f:
    json.dump(allocation_analysis, f, indent=2)
"

echo ""

# 4. 性能比较总结
echo "4. 性能比较总结..."
echo "=========================================="

python3 -c "
import json

# 读取结果
with open('$RESULTS_DIR/vanilla_results.json', 'r') as f:
    vanilla = json.load(f)

with open('$RESULTS_DIR/optimized_results.json', 'r') as f:
    optimized = json.load(f)

print('性能对比总结:')
print('==========================================')
print(f'算法配置对比:')
print(f'  Vanilla:   {vanilla[\"routing_algorithm\"]} + {vanilla[\"scheduling_algorithm\"]}')
print(f'  Optimized: {optimized[\"routing_algorithm\"]} + {optimized[\"scheduling_algorithm\"]}')
print('')

print(f'完成率对比:')
print(f'  Vanilla:   {vanilla[\"completion_rate\"]:.2%}')
print(f'  Optimized: {optimized[\"completion_rate\"]:.2%}')
improvement_rate = (optimized['completion_rate'] - vanilla['completion_rate']) / vanilla['completion_rate'] * 100
print(f'  提升:      {improvement_rate:+.2f}%')
print('')

print(f'平均响应时间对比:')
print(f'  Vanilla:   {vanilla[\"average_response_time\"]:.4f} 时间单位')
print(f'  Optimized: {optimized[\"average_response_time\"]:.4f} 时间单位')
if vanilla['average_response_time'] > 0:
    improvement_time = (vanilla['average_response_time'] - optimized['average_response_time']) / vanilla['average_response_time'] * 100
    print(f'  提升:      {improvement_time:+.2f}%')
print('')

print(f'吞吐量对比:')
print(f'  Vanilla:   {vanilla[\"throughput\"]:.4f} 请求/时间单位')
print(f'  Optimized: {optimized[\"throughput\"]:.4f} 请求/时间单位')
improvement_throughput = (optimized['throughput'] - vanilla['throughput']) / vanilla['throughput'] * 100
print(f'  提升:      {improvement_throughput:+.2f}%')
print('')

print(f'仿真运行时间对比:')
print(f'  Vanilla:   {vanilla[\"simulation_time\"]:.4f} 秒')
print(f'  Optimized: {optimized[\"simulation_time\"]:.4f} 秒')
print('')

# 计算总体性能提升
total_improvement = (improvement_rate + improvement_throughput) / 2
print(f'总体性能提升: {total_improvement:+.2f}%')
print('')

# 保存比较结果
comparison = {
    'vanilla': vanilla,
    'optimized': optimized,
    'improvements': {
        'completion_rate': improvement_rate,
        'response_time': improvement_time if vanilla['average_response_time'] > 0 else 0,
        'throughput': improvement_throughput,
        'total_improvement': total_improvement
    }
}

with open('$RESULTS_DIR/performance_comparison.json', 'w') as f:
    json.dump(comparison, f, indent=2)

print('所有结果已保存到: $RESULTS_DIR/')
print('文件列表:')
print('  - vanilla_results.json: Vanilla版本结果')
print('  - optimized_results.json: 优化版本结果')
print('  - detailed_allocation_analysis.json: 详细分配分析')
print('  - performance_comparison.json: 性能比较总结')
"

echo ""
echo "=========================================="
echo "准确的性能比较分析完成！"
echo "结果文件保存在: $RESULTS_DIR/"
echo "=========================================="
