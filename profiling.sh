#!/bin/bash
################################################################################
# Universal Model Profiling Script
################################################################################
# 使用方法：
#   1. 修改下面的 MODEL_NAME 变量
#   2. 运行: ./profiling.sh
#
# 此脚本会自动：
#   - 检测当前 GPU 类型
#   - 运行 MLP 和 Attention profiling
#   - 将结果放在对应的目录
#   - 验证 profiling（运行 prefill 和 decode 测试）
#   - 成功后输出 "SUCCESS!"
################################################################################

# ============================================================================
# 配置区域 - 只需修改这里
# ============================================================================
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen-7B}"  # 使用环境变量，如果未设置则默认为 Qwen/Qwen-7B
# 其他示例:
# MODEL_NAME="meta-llama/Llama-2-7b-hf"
# MODEL_NAME="meta-llama/Meta-Llama-3-8B"
# MODEL_NAME="Qwen/Qwen-72B"

# ============================================================================
# 高级配置（通常不需要修改）
# ============================================================================
NUM_GPUS=1                  # GPU 数量
TENSOR_PARALLEL=1           # Tensor Parallel 大小
MAX_TOKENS=4096            # 最大 token 数
BATCH_SIZE_TEST=2          # 验证时的 batch size
SEQ_LENGTH_TEST=128        # 验证时的序列长度
TOKENS_TO_GENERATE=4       # Decode 验证生成的 token 数

# ============================================================================
# 脚本开始 - 不要修改下面的代码
# ============================================================================

set -e  # 遇到错误立即退出

# 添加 sarathi-serve 到 Python 路径
export PYTHONPATH="/users/7/li003385/workspace/sarathi-serve:${PYTHONPATH:-}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "\n${CYAN}========================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================================================${NC}\n"
}

print_step() {
    echo -e "\n${BLUE}▶ $1${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ============================================================================
# 步骤 0: 显示配置信息
# ============================================================================
print_header "🚀 Universal Model Profiling Script"
echo -e "${CYAN}Model:${NC} $MODEL_NAME"
echo -e "${CYAN}Started at:${NC} $(date)"
echo -e "${CYAN}Hostname:${NC} $(hostname)"
echo ""

# ============================================================================
# 步骤 1: 检测 GPU 类型
# ============================================================================
print_step "Step 1: Detecting GPU Type"

if ! command -v nvidia-smi &> /dev/null; then
    print_error "nvidia-smi not found. This script requires NVIDIA GPU."
    exit 1
fi

GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1)
echo "GPU Info: $GPU_INFO"

# 检测 GPU 类型
if [[ $GPU_INFO == *"A100"* ]]; then
    GPU_TYPE="A100"
    GPU_TYPE_LOWER="a100"
elif [[ $GPU_INFO == *"H100"* ]]; then
    GPU_TYPE="H100"
    GPU_TYPE_LOWER="h100"
elif [[ $GPU_INFO == *"A40"* ]]; then
    GPU_TYPE="A40"
    GPU_TYPE_LOWER="a40"
elif [[ $GPU_INFO == *"V100"* ]]; then
    GPU_TYPE="V100"
    GPU_TYPE_LOWER="v100"
elif [[ $GPU_INFO == *"L40S"* ]] || [[ $GPU_INFO == *"L40s"* ]]; then
    GPU_TYPE="L40S"
    GPU_TYPE_LOWER="l40s"
else
    print_warning "Unknown GPU type: $GPU_INFO"
    print_warning "Defaulting to A100"
    GPU_TYPE="A100"
    GPU_TYPE_LOWER="a100"
fi

print_success "Detected GPU: $GPU_TYPE"

# 显示 GPU 状态
nvidia-smi

# ============================================================================
# 步骤 2: 检查模型配置
# ============================================================================
print_step "Step 2: Checking Model Configuration"

if ! python3 -c "
import yaml
with open('model_configs.yaml', 'r') as f:
    configs = yaml.safe_load(f)
    if 'models' in configs and '$MODEL_NAME' in configs['models']:
        print('✅ Model configuration found')
        exit(0)
    else:
        print('❌ Model configuration not found')
        exit(1)
" 2>/dev/null; then
    print_warning "Model '$MODEL_NAME' not found in model_configs.yaml"
    print_step "Please add the model configuration first or use auto_profile.py"
    exit 1
fi

# ============================================================================
# 步骤 3: 安装/验证依赖
# ============================================================================
print_step "Step 3: Verifying Dependencies"

python3 -c "
import sys
required_modules = ['tqdm', 'ray', 'pandas', 'numpy', 'torch', 'yaml']
missing = []
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print('Missing modules:', missing)
    sys.exit(1)
else:
    print('✅ All critical dependencies verified')
" || {
    print_error "Some dependencies are missing. Installing..."
    pip install -q tqdm ray pandas numpy torch pyyaml
}

# ============================================================================
# 步骤 4: 启动 Ray
# ============================================================================
print_step "Step 4: Starting Ray Cluster"

# 停止之前可能运行的 Ray
ray stop 2>/dev/null || true
sleep 2

# 启动 Ray
ray start --head --port=6379 --num-gpus=$NUM_GPUS 2>&1 | tail -5
print_success "Ray cluster started"

# ============================================================================
# 步骤 5: 运行 MLP Profiling
# ============================================================================
print_step "Step 5: Running MLP Profiling"

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
OUTPUT_DIR="profiling_outputs_${TIMESTAMP}"

echo "Output directory: $OUTPUT_DIR"
echo "Running MLP profiling..."

if python3 -m vidur.profiling.mlp.main \
    --models "$MODEL_NAME" \
    --num_gpus $NUM_GPUS \
    --num_tensor_parallel_workers $TENSOR_PARALLEL \
    --max_tokens $MAX_TOKENS \
    --output_dir "$OUTPUT_DIR"; then
    print_success "MLP profiling completed"
else
    print_error "MLP profiling failed"
    ray stop 2>&1 | tail -3
    exit 1
fi

# ============================================================================
# 步骤 6: 运行 Attention Profiling
# ============================================================================
print_step "Step 6: Running Attention Profiling"

echo "Running Attention profiling..."

if python3 -m vidur.profiling.attention.main \
    --models "$MODEL_NAME" \
    --num_gpus $NUM_GPUS \
    --num_tensor_parallel_workers $TENSOR_PARALLEL \
    --max_model_len $MAX_TOKENS \
    --max_seq_len $MAX_TOKENS \
    --output_dir "$OUTPUT_DIR"; then
    print_success "Attention profiling completed"
else
    print_error "Attention profiling failed"
    ray stop 2>&1 | tail -3
    exit 1
fi

# ============================================================================
# 步骤 7: 移动文件到正确位置
# ============================================================================
print_step "Step 7: Moving Profiling Data to Correct Location"

# 提取模型的组织名和模型名
if [[ $MODEL_NAME == *"/"* ]]; then
    ORG_NAME=$(echo $MODEL_NAME | cut -d'/' -f1)
    MODEL_SHORT=$(echo $MODEL_NAME | cut -d'/' -f2)
else
    ORG_NAME="custom"
    MODEL_SHORT=$MODEL_NAME
fi

# 目标目录
TARGET_DIR="data/profiling/compute/${GPU_TYPE_LOWER}/${ORG_NAME}/${MODEL_SHORT}"
mkdir -p "$TARGET_DIR"

# 查找并移动 CSV 文件
echo "Searching for profiling data in $OUTPUT_DIR..."
MLP_CSV=$(find "$OUTPUT_DIR" -name "mlp.csv" -type f | head -1)
ATTENTION_CSV=$(find "$OUTPUT_DIR" -name "attention.csv" -type f | head -1)

if [ -n "$MLP_CSV" ]; then
    cp "$MLP_CSV" "$TARGET_DIR/mlp.csv"
    print_success "MLP data copied to $TARGET_DIR/mlp.csv"
else
    print_error "MLP CSV file not found in $OUTPUT_DIR"
fi

if [ -n "$ATTENTION_CSV" ]; then
    cp "$ATTENTION_CSV" "$TARGET_DIR/attention.csv"
    print_success "Attention data copied to $TARGET_DIR/attention.csv"
else
    print_error "Attention CSV file not found in $OUTPUT_DIR"
fi

# 显示结果
echo ""
echo "Profiling data location:"
ls -lh "$TARGET_DIR/"

# ============================================================================
# 步骤 8: 停止 Ray
# ============================================================================
print_step "Step 8: Stopping Ray Cluster"
ray stop 2>&1 | tail -3
print_success "Ray cluster stopped"

# ============================================================================
# 步骤 9: 验证 Profiling - Prefill 测试
# ============================================================================
print_step "Step 9: Validation - Running Prefill Test"

echo "Testing with batch_size=$BATCH_SIZE_TEST, sequence_length=$SEQ_LENGTH_TEST"

if python3 run.py prefill "$MODEL_NAME" "$GPU_TYPE" \
    --batch_size $BATCH_SIZE_TEST \
    --sequence_length $SEQ_LENGTH_TEST 2>&1 | tee /tmp/prefill_test.log; then
    
    # 检查输出中是否有成功的指标
    if grep -q "Mean latency" /tmp/prefill_test.log || grep -q "mean" /tmp/prefill_test.log; then
        print_success "Prefill test PASSED"
        PREFILL_SUCCESS=true
    else
        print_error "Prefill test completed but no valid metrics found"
        PREFILL_SUCCESS=false
    fi
else
    print_error "Prefill test FAILED"
    PREFILL_SUCCESS=false
fi

# ============================================================================
# 步骤 10: 验证 Profiling - Decode 测试
# ============================================================================
print_step "Step 10: Validation - Running Decode Test"

echo "Testing with batch_size=$BATCH_SIZE_TEST, tokens_to_generate=$TOKENS_TO_GENERATE"

if python3 run.py decode "$MODEL_NAME" "$GPU_TYPE" \
    --batch_size $BATCH_SIZE_TEST \
    --tokens_to_generate $TOKENS_TO_GENERATE \
    --kv_cache_length $SEQ_LENGTH_TEST 2>&1 | tee /tmp/decode_test.log; then
    
    # 检查输出中是否有成功的指标
    if grep -q "Mean latency" /tmp/decode_test.log || grep -q "mean" /tmp/decode_test.log; then
        print_success "Decode test PASSED"
        DECODE_SUCCESS=true
    else
        print_error "Decode test completed but no valid metrics found"
        DECODE_SUCCESS=false
    fi
else
    print_error "Decode test FAILED"
    DECODE_SUCCESS=false
fi

# ============================================================================
# 最终结果
# ============================================================================
print_header "📊 Profiling Summary"

echo -e "${CYAN}Model:${NC} $MODEL_NAME"
echo -e "${CYAN}GPU:${NC} $GPU_TYPE"
echo -e "${CYAN}Data Location:${NC} $TARGET_DIR"
echo ""
echo -e "${CYAN}Results:${NC}"

if [ -f "$TARGET_DIR/mlp.csv" ]; then
    echo -e "  ${GREEN}✅${NC} MLP profiling data: $(wc -l < "$TARGET_DIR/mlp.csv") lines"
else
    echo -e "  ${RED}❌${NC} MLP profiling data: MISSING"
fi

if [ -f "$TARGET_DIR/attention.csv" ]; then
    echo -e "  ${GREEN}✅${NC} Attention profiling data: $(wc -l < "$TARGET_DIR/attention.csv") lines"
else
    echo -e "  ${RED}❌${NC} Attention profiling data: MISSING"
fi

if [ "$PREFILL_SUCCESS" = true ]; then
    echo -e "  ${GREEN}✅${NC} Prefill validation: PASSED"
else
    echo -e "  ${RED}❌${NC} Prefill validation: FAILED"
fi

if [ "$DECODE_SUCCESS" = true ]; then
    echo -e "  ${GREEN}✅${NC} Decode validation: PASSED"
else
    echo -e "  ${RED}❌${NC} Decode validation: FAILED"
fi

echo ""

# 检查是否所有测试都通过
if [ -f "$TARGET_DIR/mlp.csv" ] && \
   [ -f "$TARGET_DIR/attention.csv" ] && \
   [ "$PREFILL_SUCCESS" = true ] && \
   [ "$DECODE_SUCCESS" = true ]; then
    
    print_header "🎉 SUCCESS! 🎉"
    echo -e "${GREEN}All profiling and validation tests passed!${NC}"
    echo ""
    echo -e "${CYAN}You can now use this model for simulations:${NC}"
    echo ""
    echo -e "  ${YELLOW}# Prefill simulation${NC}"
    echo "  python3 run.py prefill \"$MODEL_NAME\" $GPU_TYPE --batch_size 4 --sequence_length 256"
    echo ""
    echo -e "  ${YELLOW}# Decode simulation${NC}"
    echo "  python3 run.py decode \"$MODEL_NAME\" $GPU_TYPE --batch_size 8 --tokens_to_generate 10 --kv_cache_length 256"
    echo ""
    
    # 清理临时文件
    rm -f /tmp/prefill_test.log /tmp/decode_test.log
    
    print_header "Completed at: $(date)"
    
    echo ""
    echo -e "${GREEN}${BOLD}███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗██╗${NC}"
    echo -e "${GREEN}${BOLD}██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝██║${NC}"
    echo -e "${GREEN}${BOLD}███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗██║${NC}"
    echo -e "${GREEN}${BOLD}╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║╚═╝${NC}"
    echo -e "${GREEN}${BOLD}███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║██╗${NC}"
    echo -e "${GREEN}${BOLD}╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝╚═╝${NC}"
    echo ""
    
    exit 0
else
    print_header "❌ PROFILING INCOMPLETE"
    echo -e "${RED}Some profiling steps or validation tests failed.${NC}"
    echo ""
    echo -e "${YELLOW}Please check the logs above for details.${NC}"
    echo ""
    echo -e "${YELLOW}Common issues:${NC}"
    echo "  1. Model configuration missing or incorrect"
    echo "  2. Insufficient GPU memory"
    echo "  3. Missing dependencies (check sarathi-serve)"
    echo "  4. Profiling data not generated correctly"
    echo ""
    
    # 清理临时文件
    rm -f /tmp/prefill_test.log /tmp/decode_test.log
    
    exit 1
fi

