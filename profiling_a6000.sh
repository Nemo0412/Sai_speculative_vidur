#!/bin/bash

################################################################################
# A6000 GPU Profiling Script for Small Models
################################################################################
# 用途: 在 A6000 GPU 上对小模型 (< 10B) 进行 profiling
# 
# 使用方法:
#   1. 直接运行（如果在交互式节点上）:
#      bash profiling_a6000.sh
#
#   2. 或通过 SLURM 提交（如果需要）:
#      sbatch --gres=gpu:a6000:1 --partition=<partition_name> profiling_a6000.sh
#
# 说明:
#   - 脚本会自动设置环境
#   - 依次对每个小模型进行 profiling
#   - 结果保存到 data/profiling/compute/a6000/<model_name>/
#   - 可以随时 Ctrl+C 中断，已完成的模型数据会保存
################################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 小模型列表 (< 10B parameters)
SMALL_MODELS=(
    "Qwen/Qwen-7B"
    "codellama/CodeLlama-7b-Instruct-hf"
    "meta-llama/Llama-3.1-8B-Instruct"
    "meta-llama/Llama-3.2-1B-Instruct"
)

# GPU 设备类型
GPU_DEVICE="a6000"

# 工作目录
WORK_DIR="/users/7/li003385/workspace/Sai_speculative_vidur"
SARATHI_DIR="/users/7/li003385/workspace/sarathi-serve"

# 创建日志目录
mkdir -p logs

# 日志文件
LOG_FILE="logs/profiling_a6000_$(date +%Y%m%d_%H%M%S).log"
exec &> >(tee -a "$LOG_FILE")

################################################################################
# 环境检查和设置
################################################################################

log_info "=========================================="
log_info "A6000 Profiling Script Started"
log_info "=========================================="
log_info "Timestamp: $(date)"
log_info "Hostname: $(hostname)"
log_info "Working directory: $WORK_DIR"
log_info "Log file: $LOG_FILE"
echo ""

# 检查是否在正确的目录
if [ ! -f "environment.yaml" ]; then
    log_error "environment.yaml not found. Please run from: $WORK_DIR"
    exit 1
fi

# 检查 GPU
log_info "Checking GPU availability..."
if ! nvidia-smi > /dev/null 2>&1; then
    log_error "nvidia-smi not available. Please ensure you are on a GPU node."
    exit 1
fi

echo ""
nvidia-smi
echo ""

# 检查是否是 A6000
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
log_info "Detected GPU: $GPU_NAME"

if [[ ! "$GPU_NAME" =~ "A6000" ]]; then
    log_warning "This script is designed for A6000. Detected: $GPU_NAME"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Aborted by user"
        exit 0
    fi
fi

################################################################################
# 加载模块
################################################################################

log_info "=========================================="
log_info "Loading Modules"
log_info "=========================================="

# 加载 CUDA
if command -v module &> /dev/null; then
    log_info "Loading CUDA 12.1.1..."
    module load cuda/12.1.1
    
    log_info "Loading GCC 11.3.0..."
    module load gcc/11.3.0
    gcc --version
else
    log_warning "module command not available, assuming environment is pre-configured"
fi

echo ""

################################################################################
# 初始化 Conda
################################################################################

log_info "=========================================="
log_info "Initializing Conda Environment"
log_info "=========================================="

__conda_setup="$('/users/7/li003385/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/users/7/li003385/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/users/7/li003385/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/users/7/li003385/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup

# 创建或激活 conda 环境
if ! conda env list | grep -q "^vidur "; then
    log_info "Creating vidur conda environment..."
    conda env create -f environment.yaml -y
else
    log_info "Vidur environment already exists"
fi

log_info "Activating vidur environment..."
conda activate vidur

log_info "Python version: $(python --version)"
log_info "Python location: $(which python)"
log_info "Conda environment: $CONDA_DEFAULT_ENV"
echo ""

################################################################################
# 安装 sarathi-serve
################################################################################

log_info "=========================================="
log_info "Setting up sarathi-serve"
log_info "=========================================="

cd /users/7/li003385/workspace

if [ ! -d "sarathi-serve" ]; then
    log_info "Cloning sarathi-serve..."
    git clone https://github.com/microsoft/sarathi-serve
    cd sarathi-serve
    log_info "Checking out vidur branch..."
    git checkout vidur
else
    cd sarathi-serve
    log_info "sarathi-serve already exists, pulling latest..."
    git checkout vidur
    git pull origin vidur || true
fi

# 修改 setup.py
if [ -f "setup.py" ]; then
    log_info "Patching setup.py for PyTorch compatibility..."
    cp setup.py setup.py.bak 2>/dev/null || true
    sed -i 's/torch==2\.3/torch>=2.3/g' setup.py || true
    sed -i 's/torch>=2\.3,<2\.4/torch>=2.3/g' setup.py || true
fi

# 检查是否已安装
if python -c "import flashinfer; import sarathi" 2>/dev/null; then
    log_success "sarathi-serve and flashinfer already installed"
    python -c "import flashinfer; print('flashinfer version:', flashinfer.__version__)"
else
    log_info "Installing sarathi-serve..."
    log_info "This will compile C++ extensions and install flashinfer..."
    
    # 安装 sarathi-serve
    MAX_JOBS=4 pip install -e . --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ 2>&1 | tail -30
    
    # 确保 flashinfer 版本正确
    log_info "Ensuring flashinfer 0.1.6 is installed..."
    pip install "flashinfer==0.1.6+cu121torch2.3" --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ --force-reinstall --no-deps 2>&1 | tail -5
    
    # 验证安装
    if python -c "import flashinfer; import sarathi; from sarathi import pos_encoding_ops" 2>/dev/null; then
        log_success "sarathi-serve installed successfully"
        python -c "import flashinfer; print('flashinfer version:', flashinfer.__version__)"
    else
        log_error "sarathi-serve installation failed"
        log_info "Attempting alternative installation..."
        MAX_JOBS=4 pip install --force-reinstall -e . --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ 2>&1 | tail -30
        
        if ! python -c "import flashinfer; import sarathi" 2>/dev/null; then
            log_error "Installation failed. Please check the logs."
            exit 1
        fi
    fi
fi

echo ""

################################################################################
# 安装 Vidur
################################################################################

cd "$WORK_DIR"

log_info "=========================================="
log_info "Installing Vidur"
log_info "=========================================="

pip install -e . -q
log_success "Vidur installed"
echo ""

################################################################################
# Profiling 函数
################################################################################

profile_model() {
    local model_name=$1
    local model_short_name=$(echo "$model_name" | rev | cut -d'/' -f1 | rev)
    
    log_info "=========================================="
    log_info "Profiling: $model_name"
    log_info "=========================================="
    log_info "Started at: $(date)"
    
    # 检查是否已存在数据
    local output_dir="data/profiling/compute/$GPU_DEVICE/$model_name"
    if [ -f "$output_dir/mlp.csv" ] && [ -f "$output_dir/attention.csv" ]; then
        local mlp_lines=$(wc -l < "$output_dir/mlp.csv")
        local attn_lines=$(wc -l < "$output_dir/attention.csv")
        
        if [ "$mlp_lines" -gt 100 ] && [ "$attn_lines" -gt 1000 ]; then
            log_warning "Profiling data already exists for $model_name"
            log_info "  mlp.csv: $mlp_lines lines"
            log_info "  attention.csv: $attn_lines lines"
            read -p "Skip this model? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                log_info "Skipping $model_name"
                return 0
            fi
        fi
    fi
    
    # 运行 profiling
    log_info "Running profiling command..."
    
    if python -m vidur.profiling.profiler \
        --model_name "$model_name" \
        --device "$GPU_DEVICE" \
        --output_dir "data/profiling" 2>&1 | tee "logs/profile_${GPU_DEVICE}_${model_short_name}.log"; then
        
        log_success "Profiling completed for $model_name"
        
        # 验证输出
        if [ -f "$output_dir/mlp.csv" ] && [ -f "$output_dir/attention.csv" ]; then
            local mlp_lines=$(wc -l < "$output_dir/mlp.csv")
            local attn_lines=$(wc -l < "$output_dir/attention.csv")
            log_success "Generated files:"
            log_success "  mlp.csv: $mlp_lines lines"
            log_success "  attention.csv: $attn_lines lines"
        else
            log_warning "Output files not found, but profiling command succeeded"
        fi
        
        return 0
    else
        log_error "Profiling failed for $model_name"
        return 1
    fi
}

################################################################################
# 主循环 - Profile 所有小模型
################################################################################

log_info "=========================================="
log_info "Starting Profiling for Small Models on A6000"
log_info "=========================================="
log_info "Total models: ${#SMALL_MODELS[@]}"
echo ""

# 统计
TOTAL_MODELS=${#SMALL_MODELS[@]}
SUCCESS_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0

# 记录开始时间
START_TIME=$(date +%s)

# 遍历所有模型
for i in "${!SMALL_MODELS[@]}"; do
    model="${SMALL_MODELS[$i]}"
    model_num=$((i + 1))
    
    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Model $model_num/$TOTAL_MODELS: $model"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if profile_model "$model"; then
        ((SUCCESS_COUNT++))
    else
        ((FAILED_COUNT++))
        log_warning "Continuing to next model..."
    fi
    
    # 显示进度
    echo ""
    log_info "Progress: $model_num/$TOTAL_MODELS completed"
    log_info "Success: $SUCCESS_COUNT | Failed: $FAILED_COUNT"
    echo ""
done

# 记录结束时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
HOURS=$((DURATION / 3600))
MINUTES=$(((DURATION % 3600) / 60))
SECONDS=$((DURATION % 60))

################################################################################
# 最终报告
################################################################################

echo ""
echo ""
log_info "╔══════════════════════════════════════════════════════════╗"
log_info "║         A6000 Profiling Complete                         ║"
log_info "╚══════════════════════════════════════════════════════════╝"
echo ""
log_info "Summary:"
log_info "  Total models:    $TOTAL_MODELS"
log_success "  Successful:      $SUCCESS_COUNT"
log_error "  Failed:          $FAILED_COUNT"
log_info "  Duration:        ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo ""
log_info "Output directory: data/profiling/compute/$GPU_DEVICE/"
log_info "Log file:        $LOG_FILE"
echo ""

# 列出生成的数据
log_info "Generated profiling data:"
for model in "${SMALL_MODELS[@]}"; do
    output_dir="data/profiling/compute/$GPU_DEVICE/$model"
    if [ -f "$output_dir/mlp.csv" ] && [ -f "$output_dir/attention.csv" ]; then
        mlp_lines=$(wc -l < "$output_dir/mlp.csv")
        attn_lines=$(wc -l < "$output_dir/attention.csv")
        log_success "  ✓ $model"
        log_info "    mlp.csv: $mlp_lines lines, attention.csv: $attn_lines lines"
    else
        log_error "  ✗ $model (files not found)"
    fi
done

echo ""
log_info "=========================================="
log_info "Finished at: $(date)"
log_info "=========================================="

# 退出码
if [ $FAILED_COUNT -eq 0 ]; then
    log_success "All models profiled successfully!"
    exit 0
else
    log_warning "Some models failed. Check logs for details."
    exit 1
fi

