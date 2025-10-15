#!/bin/bash
#SBATCH --job-name=vidur_validation_test
#SBATCH --partition=interactive-gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=01:00:00
#SBATCH --output=logs/validation_test_%j.out
#SBATCH --error=logs/validation_test_%j.err

echo "=========================================="
echo "Vidur Validation Test - Prefill & Decode"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"
echo ""

# 加载 CUDA
module load cuda/12.1.1

# 激活 conda 环境
echo "激活 vidur 环境..."
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

conda activate vidur

# 检查 GPU
echo "检查 GPU..."
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
echo ""

cd /users/7/li003385/workspace/Sai_speculative_vidur

# 清理之前的测试输出
rm -rf test_output_prefill test_output_decode

# 1. 测试 Prefill
echo "=========================================="
echo "1. 测试 Prefill"
echo "=========================================="
echo "运行命令: python3 run.py prefill Qwen/Qwen-7B A40 --batch_size 4 --sequence_length 256"
echo ""

python3 run.py prefill Qwen/Qwen-7B A40 --batch_size 4 --sequence_length 256 --output_dir test_output_prefill

PREFILL_STATUS=$?

if [ $PREFILL_STATUS -eq 0 ]; then
    echo ""
    echo "✅ Prefill 测试成功！"
    echo ""
    # 显示输出文件
    echo "Prefill 输出文件:"
    ls -lh test_output_prefill/*/
else
    echo ""
    echo "❌ Prefill 测试失败 (退出码: $PREFILL_STATUS)"
fi

echo ""
echo "=========================================="
echo "2. 测试 Decode"
echo "=========================================="
echo "运行命令: python3 run.py decode Qwen/Qwen-7B A40 --batch_size 8 --tokens_to_generate 4 --kv_cache_length 1024"
echo ""

python3 run.py decode Qwen/Qwen-7B A40 --batch_size 8 --tokens_to_generate 4 --kv_cache_length 1024 --output_dir test_output_decode

DECODE_STATUS=$?

if [ $DECODE_STATUS -eq 0 ]; then
    echo ""
    echo "✅ Decode 测试成功！"
    echo ""
    # 显示输出文件
    echo "Decode 输出文件:"
    ls -lh test_output_decode/*/
else
    echo ""
    echo "❌ Decode 测试失败 (退出码: $DECODE_STATUS)"
fi

echo ""
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo "Prefill 测试: $([ $PREFILL_STATUS -eq 0 ] && echo '✅ 成功' || echo '❌ 失败')"
echo "Decode 测试: $([ $DECODE_STATUS -eq 0 ] && echo '✅ 成功' || echo '❌ 失败')"
echo ""

if [ $PREFILL_STATUS -eq 0 ] && [ $DECODE_STATUS -eq 0 ]; then
    echo "🎉 SUCCESS! 所有测试通过！"
    echo ""
    echo "结果位置:"
    echo "  Prefill: test_output_prefill/"
    echo "  Decode:  test_output_decode/"
    exit 0
else
    echo "❌ 部分测试失败"
    exit 1
fi

echo ""
echo "End time: $(date)"

