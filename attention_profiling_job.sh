#!/bin/bash
#SBATCH --job-name=attention_profiling
#SBATCH --output=logs/attention_%j.out
#SBATCH --error=logs/attention_%j.err
#SBATCH --partition=interactive-gpu
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

################################################################################
# Attention Profiling for Qwen/Qwen-7B on A40
################################################################################

# 创建 logs 目录
mkdir -p logs

# 加载 CUDA 模块
module load cuda/12.1.1

# 加载更新的 GCC (sarathi C++ 扩展需要 GCC 9+)
echo "Loading GCC 11.3.0 for C++ compilation..."
module load gcc/11.3.0
gcc --version

# 初始化 conda
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

# 打印作业信息
echo "========================================"
echo "Attention Profiling Job"
echo "Job ID: $SLURM_JOB_ID"
echo "Started at: $(date)"
echo "Running on node: $(hostname)"
echo "========================================"
echo ""

# 激活 conda 环境
echo "Activating vidur environment..."
conda activate vidur

echo "Python version:"
python --version
echo "Python location:"
which python
echo "flashinfer version:"
python -c "import flashinfer; print(flashinfer.__version__)"
echo ""

# 添加 sarathi-serve 到 Python 路径
export PYTHONPATH="/users/7/li003385/workspace/sarathi-serve:${PYTHONPATH:-}"

# 切换到工作目录
cd /users/7/li003385/workspace/Sai_speculative_vidur

# 运行 Attention Profiling
echo "========================================"
echo "Running Attention Profiling"
echo "========================================"
echo "Model: Qwen/Qwen-7B"
echo "GPU: 1"
echo "Output directory: profiling_outputs/"
echo ""

python -m vidur.profiling.attention.main \
    --models Qwen/Qwen-7B \
    --num_gpus 1

EXIT_CODE=$?

echo ""
echo "========================================"
echo "Job completed at: $(date)"
echo "Exit code: $EXIT_CODE"
echo "========================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Attention profiling completed successfully!"
    echo ""
    echo "Output files:"
    find profiling_outputs -name "attention.csv" -newer logs/attention_$SLURM_JOB_ID.out 2>/dev/null | head -5
fi

exit $EXIT_CODE

