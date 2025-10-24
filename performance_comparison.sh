#!/bin/bash

# Performance Comparison Script
# 性能比较脚本 - 比较vanilla版本和优化版本

echo "=========================================="
echo "调度算法性能比较分析"
echo "=========================================="

# 创建结果目录
mkdir -p results
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="results/performance_${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo "结果将保存到: $RESULTS_DIR"
echo ""

# 1. Vanilla版本测试 (基础配置)
echo "1. 测试Vanilla版本 (基础配置)..."
echo "----------------------------------------"

# 设置vanilla配置
cat > config_vanilla.py << 'EOF'
"""
Vanilla configuration - 基础配置
"""
# System Configuration
K_DRAFT_MODELS = 20
N_TARGET_MODELS = 4
ROUTER_QUEUE_SIZE = 50

# Target Model Configuration - 基础配置
TARGET_CONFIGS = [
    {"queue_size": 20, "batch_size": 5},  # Target 0
    {"queue_size": 15, "batch_size": 4},  # Target 1
    {"queue_size": 25, "batch_size": 6},  # Target 2
    {"queue_size": 18, "batch_size": 4},  # Target 3
]

# 简化的处理时间 - 所有draft到所有target都是相同时间
PREFILL_TIMES = [[2.0, 2.0, 2.0, 2.0] for _ in range(20)]
DECODE_TIMES = [[1.0, 1.0, 1.0, 1.0] for _ in range(20)]

# Simulation Configuration
SIMULATION_TIME = 100.0
REQUEST_ARRIVAL_RATE = 1.0

# 基础算法配置
ROUTING_ALGORITHM = "round_robin"  # 简单轮询
SCHEDULING_ALGORITHM = "fifo"      # 先进先出

def validate_config():
    """Validate configuration parameters."""
    assert K_DRAFT_MODELS > 0, "K_DRAFT_MODELS must be positive"
    assert N_TARGET_MODELS > 0, "N_TARGET_MODELS must be positive"
    assert ROUTER_QUEUE_SIZE > 0, "ROUTER_QUEUE_SIZE must be positive"
    assert len(TARGET_CONFIGS) == N_TARGET_MODELS, "TARGET_CONFIGS length must match N_TARGET_MODELS"
    
    for i, config in enumerate(TARGET_CONFIGS):
        assert config["queue_size"] > 0, f"Target {i} queue_size must be positive"
        assert config["batch_size"] > 0, f"Target {i} batch_size must be positive"
        assert config["batch_size"] <= config["queue_size"], f"Target {i} batch_size must be <= queue_size"
    
    assert len(PREFILL_TIMES) == K_DRAFT_MODELS, "PREFILL_TIMES must have K_DRAFT_MODELS rows"
    assert len(DECODE_TIMES) == K_DRAFT_MODELS, "DECODE_TIMES must have K_DRAFT_MODELS rows"
    
    for i, row in enumerate(PREFILL_TIMES):
        assert len(row) == N_TARGET_MODELS, f"PREFILL_TIMES row {i} must have N_TARGET_MODELS columns"
        assert all(t > 0 for t in row), f"PREFILL_TIMES row {i} must have positive values"
    
    for i, row in enumerate(DECODE_TIMES):
        assert len(row) == N_TARGET_MODELS, f"DECODE_TIMES row {i} must have N_TARGET_MODELS columns"
        assert all(t > 0 for t in row), f"DECODE_TIMES row {i} must have positive values"
EOF

# 运行vanilla测试
python3 -c "
import sys
sys.path.append('.')
import config_vanilla as config
import simulation
import json
import time

# 备份原始配置
import config as original_config
original_routing = original_config.ROUTING_ALGORITHM
original_scheduling = original_config.SCHEDULING_ALGORITHM
original_prefill = original_config.PREFILL_TIMES
original_decode = original_config.DECODE_TIMES

try:
    # 使用vanilla配置
    original_config.ROUTING_ALGORITHM = config.ROUTING_ALGORITHM
    original_config.SCHEDULING_ALGORITHM = config.SCHEDULING_ALGORITHM
    original_config.PREFILL_TIMES = config.PREFILL_TIMES
    original_config.DECODE_TIMES = config.DECODE_TIMES
    
    start_time = time.time()
    sim = simulation.SchedulingSimulation()
    result = sim.run_simulation(simulation_time=100.0)
    vanilla_time = time.time() - start_time
    
    print(f'Vanilla版本结果:')
    print(f'  总请求数: {result.total_requests}')
    print(f'  完成请求数: {result.completed_requests}')
    print(f'  完成率: {result.completion_rate:.2%}')
    print(f'  平均响应时间: {result.average_response_time:.4f}')
    print(f'  吞吐量: {result.throughput:.4f}')
    print(f'  仿真运行时间: {vanilla_time:.4f}秒')
    
    # 保存结果
    vanilla_results = {
        'version': 'vanilla',
        'routing_algorithm': config.ROUTING_ALGORITHM,
        'scheduling_algorithm': config.SCHEDULING_ALGORITHM,
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
    original_config.ROUTING_ALGORITHM = original_routing
    original_config.SCHEDULING_ALGORITHM = original_scheduling
    original_config.PREFILL_TIMES = original_prefill
    original_config.DECODE_TIMES = original_decode
"

echo ""

# 2. 优化版本测试
echo "2. 测试优化版本 (最佳算法配置)..."
echo "----------------------------------------"

python3 -c "
import sys
sys.path.append('.')
import config
import simulation
import json
import time

# 使用优化配置
config.ROUTING_ALGORITHM = 'least_loaded'
config.SCHEDULING_ALGORITHM = 'priority'

start_time = time.time()
sim = simulation.SchedulingSimulation()
result = sim.run_simulation(simulation_time=100.0)
optimized_time = time.time() - start_time

print(f'优化版本结果:')
print(f'  总请求数: {result.total_requests}')
print(f'  完成请求数: {result.completed_requests}')
print(f'  完成率: {result.completion_rate:.2%}')
print(f'  平均响应时间: {result.average_response_time:.4f}')
print(f'  吞吐量: {result.throughput:.4f}')
print(f'  仿真运行时间: {optimized_time:.4f}秒')

# 保存结果
optimized_results = {
    'version': 'optimized',
    'routing_algorithm': config.ROUTING_ALGORITHM,
    'scheduling_algorithm': config.SCHEDULING_ALGORITHM,
    'total_requests': result.total_requests,
    'completed_requests': result.completed_requests,
    'completion_rate': result.completion_rate,
    'average_response_time': result.average_response_time,
    'throughput': result.throughput,
    'simulation_time': optimized_time
}

with open('$RESULTS_DIR/optimized_results.json', 'w') as f:
    json.dump(optimized_results, f, indent=2)
"

echo ""

# 3. 算法分配分析
echo "3. 分析Draft和Target分配模式..."
echo "----------------------------------------"

python3 -c "
import sys
sys.path.append('.')
import config
import simulation
import json
from collections import defaultdict

# 创建分配分析器
class AllocationAnalyzer:
    def __init__(self):
        self.draft_to_target = defaultdict(list)
        self.target_load = defaultdict(int)
        self.request_types = defaultdict(int)
    
    def analyze_request(self, request):
        if request.target_model_id is not None:
            self.draft_to_target[request.draft_model_id].append(request.target_model_id)
            self.target_load[request.target_model_id] += 1
            self.request_types[request.request_type.value] += 1

# 运行分析
sim = simulation.SchedulingSimulation()
analyzer = AllocationAnalyzer()

# 修改simulation以收集分配数据
original_process = sim._finish_remaining_requests
def process_with_analysis():
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

sim._finish_remaining_requests = process_with_analysis

# 运行仿真
result = sim.run_simulation(simulation_time=50.0)

# 分析结果
print('Draft到Target分配分析:')
for draft_id in range(20):
    targets = analyzer.draft_to_target[draft_id]
    if targets:
        target_counts = {i: targets.count(i) for i in range(4)}
        print(f'  Draft {draft_id:2d}: {dict(target_counts)}')

print('')
print('Target负载分布:')
for target_id in range(4):
    load = analyzer.target_load[target_id]
    print(f'  Target {target_id}: {load} 个请求')

print('')
print('请求类型分布:')
for req_type, count in analyzer.request_types.items():
    print(f'  {req_type}: {count} 个请求')

# 保存分配分析
allocation_analysis = {
    'draft_to_target': dict(analyzer.draft_to_target),
    'target_load': dict(analyzer.target_load),
    'request_types': dict(analyzer.request_types)
}

with open('$RESULTS_DIR/allocation_analysis.json', 'w') as f:
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

print('性能对比:')
print('----------------------------------------')
print(f'配置对比:')
print(f'  Vanilla:   {vanilla[\"routing_algorithm\"]} + {vanilla[\"scheduling_algorithm\"]}')
print(f'  Optimized: {optimized[\"routing_algorithm\"]} + {optimized[\"scheduling_algorithm\"]}')
print('')

print(f'完成率对比:')
print(f'  Vanilla:   {vanilla[\"completion_rate\"]:.2%}')
print(f'  Optimized: {optimized[\"completion_rate\"]:.2%}')
improvement_rate = (optimized['completion_rate'] - vanilla['completion_rate']) / vanilla['completion_rate'] * 100
print(f'  提升:      {improvement_rate:+.2f}%')
print('')

print(f'响应时间对比:')
print(f'  Vanilla:   {vanilla[\"average_response_time\"]:.4f}')
print(f'  Optimized: {optimized[\"average_response_time\"]:.4f}')
if vanilla['average_response_time'] > 0:
    improvement_time = (vanilla['average_response_time'] - optimized['average_response_time']) / vanilla['average_response_time'] * 100
    print(f'  提升:      {improvement_time:+.2f}%')
print('')

print(f'吞吐量对比:')
print(f'  Vanilla:   {vanilla[\"throughput\"]:.4f}')
print(f'  Optimized: {optimized[\"throughput\"]:.4f}')
improvement_throughput = (optimized['throughput'] - vanilla['throughput']) / vanilla['throughput'] * 100
print(f'  提升:      {improvement_throughput:+.2f}%')
print('')

print(f'仿真运行时间对比:')
print(f'  Vanilla:   {vanilla[\"simulation_time\"]:.4f}秒')
print(f'  Optimized: {optimized[\"simulation_time\"]:.4f}秒')
print('')

# 保存比较结果
comparison = {
    'vanilla': vanilla,
    'optimized': optimized,
    'improvements': {
        'completion_rate': improvement_rate,
        'response_time': improvement_time if vanilla['average_response_time'] > 0 else 0,
        'throughput': improvement_throughput
    }
}

with open('$RESULTS_DIR/performance_comparison.json', 'w') as f:
    json.dump(comparison, f, indent=2)

print('所有结果已保存到: $RESULTS_DIR/')
"

echo ""
echo "=========================================="
echo "性能比较分析完成！"
echo "结果文件保存在: $RESULTS_DIR/"
echo "=========================================="

# 清理临时文件
rm -f config_vanilla.py
