#!/bin/bash

# 极端差异配置测试脚本
echo "=========================================="
echo "极端差异配置性能测试"
echo "=========================================="

# 创建结果目录
mkdir -p results
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="results/extreme_test_${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo "结果将保存到: $RESULTS_DIR"
echo ""

# 1. 应用极端配置
echo "1. 应用极端差异配置..."
echo "----------------------------------------"

python3 -c "
import sys
sys.path.append('.')
import extreme_config
extreme_config.create_extreme_config()
print('✅ 极端配置已应用')
"

echo ""

# 2. 测试Vanilla版本 (round_robin + fifo)
echo "2. 测试Vanilla版本 (round_robin + fifo)..."
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
    result = sim.run_simulation(simulation_time=60.0)
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

# 3. 测试优化版本 (least_loaded + shortest_job_first)
echo "3. 测试优化版本 (least_loaded + shortest_job_first)..."
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
    config.SCHEDULING_ALGORITHM = 'shortest_job_first'
    
    start_time = time.time()
    sim = simulation.SchedulingSimulation()
    result = sim.run_simulation(simulation_time=60.0)
    optimized_time = time.time() - start_time
    
    print(f'优化版本结果 (least_loaded + shortest_job_first):')
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
        'scheduling_algorithm': 'shortest_job_first',
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

# 4. 测试所有算法组合
echo "4. 测试所有算法组合..."
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
    
    all_results = {}
    
    for routing, scheduling in algorithms:
        print(f'测试: {routing} + {scheduling}')
        
        config.ROUTING_ALGORITHM = routing
        config.SCHEDULING_ALGORITHM = scheduling
        
        sim = simulation.SchedulingSimulation()
        result = sim.run_simulation(simulation_time=30.0)
        
        all_results[f'{routing}_{scheduling}'] = {
            'routing': routing,
            'scheduling': scheduling,
            'completion_rate': result.completion_rate,
            'average_response_time': result.average_response_time,
            'throughput': result.throughput,
            'total_requests': result.total_requests,
            'completed_requests': result.completed_requests
        }
        
        print(f'  完成率: {result.completion_rate:.2%}')
        print(f'  响应时间: {result.average_response_time:.4f}')
        print(f'  吞吐量: {result.throughput:.4f}')
    
    # 找出最佳配置
    best_completion = max(all_results.items(), key=lambda x: x[1]['completion_rate'])
    best_response = min(all_results.items(), key=lambda x: x[1]['average_response_time'])
    best_throughput = max(all_results.items(), key=lambda x: x[1]['throughput'])
    
    print(f'\\n最佳完成率: {best_completion[0]} - {best_completion[1][\"completion_rate\"]:.2%}')
    print(f'最佳响应时间: {best_response[0]} - {best_response[1][\"average_response_time\"]:.4f}')
    print(f'最佳吞吐量: {best_throughput[0]} - {best_throughput[1][\"throughput\"]:.4f}')
    
    # 计算性能差异
    completion_rates = [r['completion_rate'] for r in all_results.values()]
    response_times = [r['average_response_time'] for r in all_results.values()]
    throughputs = [r['throughput'] for r in all_results.values()]
    
    completion_range = max(completion_rates) - min(completion_rates)
    response_range = max(response_times) - min(response_times)
    throughput_range = max(throughputs) - min(throughputs)
    
    print(f'\\n性能差异范围:')
    print(f'完成率差异: {completion_range:.2%}')
    print(f'响应时间差异: {response_range:.4f}')
    print(f'吞吐量差异: {throughput_range:.4f}')
    
    if completion_range > 0.15:  # 15%以上差异
        print('✅ 算法差异显著！')
    elif completion_range > 0.1:  # 10%以上差异
        print('⚠️ 算法差异中等')
    else:
        print('❌ 算法差异仍然较小')
    
    # 保存所有结果
    with open('$RESULTS_DIR/all_algorithm_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
        
finally:
    # 恢复原始配置
    config.ROUTING_ALGORITHM = original_routing
    config.SCHEDULING_ALGORITHM = original_scheduling
"

echo ""

# 5. 性能比较总结
echo "5. 性能比较总结..."
echo "=========================================="

python3 -c "
import json

# 读取结果
with open('$RESULTS_DIR/vanilla_results.json', 'r') as f:
    vanilla = json.load(f)

with open('$RESULTS_DIR/optimized_results.json', 'r') as f:
    optimized = json.load(f)

print('极端配置下的性能对比:')
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

if total_improvement > 15:
    print('🎉 极端配置下算法差异显著！')
elif total_improvement > 10:
    print('✅ 极端配置下算法差异明显')
elif total_improvement > 5:
    print('⚠️ 极端配置下算法差异中等')
else:
    print('❌ 即使极端配置下算法差异仍然较小')

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

with open('$RESULTS_DIR/extreme_performance_comparison.json', 'w') as f:
    json.dump(comparison, f, indent=2)

print('\\n所有结果已保存到: $RESULTS_DIR/')
print('文件列表:')
print('  - vanilla_results.json: Vanilla版本结果')
print('  - optimized_results.json: 优化版本结果')
print('  - all_algorithm_results.json: 所有算法组合结果')
print('  - extreme_performance_comparison.json: 极端配置性能比较')
"

echo ""
echo "=========================================="
echo "极端差异配置测试完成！"
echo "结果文件保存在: $RESULTS_DIR/"
echo "=========================================="
