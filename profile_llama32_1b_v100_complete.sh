#!/bin/bash
#SBATCH --job-name=llama32-v100-full
#SBATCH --partition=v100
#SBATCH --gres=gpu:v100:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=01:30:00
#SBATCH --output=logs/profiling_llama32_1b_v100_complete_%j.out
#SBATCH --error=logs/profiling_llama32_1b_v100_complete_%j.err

################################################################################
# 完整的 V100 Profiling: MLP + Attention (PyTorch Native)
# 模型: meta-llama/Llama-3.2-1B-Instruct
################################################################################

mkdir -p logs

# 加载模块
module load cuda/12.1.1
module load gcc/11.3.0

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

# 激活环境
conda activate vidur

echo "========================================"
echo "V100 完整 Profiling"
echo "模型: meta-llama/Llama-3.2-1B-Instruct"
echo "Job ID: $SLURM_JOB_ID"
echo "Started at: $(date)"
echo "Running on node: $(hostname)"
echo "========================================"
echo ""

# 检测 GPU
nvidia-smi
echo ""

# 登录 Hugging Face
echo "========================================"
echo "Logging in to Hugging Face"
echo "========================================"
# HF_TOKEN should be set as environment variable or passed as parameter
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  HF_TOKEN not set, skipping Hugging Face login"
else
    python3 << EOF
from huggingface_hub import login
login(token="$HF_TOKEN")
print("✅ Logged in to Hugging Face")
EOF
fi
echo ""

# 切换到工作目录
cd /users/7/li003385/workspace/Sai_speculative_vidur

# 模型配置
MODEL_NAME="meta-llama/Llama-3.2-1B-Instruct"
N_EMBD=2048
N_Q_HEAD=32
N_KV_HEAD=8
OUTPUT_DIR="data/profiling/compute/v100/meta-llama/Llama-3.2-1B-Instruct"

mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "Step 1: MLP Profiling"
echo "========================================"

# 安装 sarathi-serve (如果需要)
cd /users/7/li003385/workspace
if [ ! -d "sarathi-serve" ]; then
    git clone https://github.com/microsoft/sarathi-serve
    cd sarathi-serve
    git checkout vidur
else
    cd sarathi-serve
    git checkout vidur
    git pull origin vidur || true
fi

# 修改 setup.py
if [ -f "setup.py" ]; then
    cp setup.py setup.py.bak 2>/dev/null || true
    sed -i 's/torch==2\.3/torch>=2.3/g' setup.py || true
    sed -i 's/torch>=2\.3,<2\.4/torch>=2.3/g' setup.py || true
fi

MAX_JOBS=4 pip install -e . --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ 2>&1 | tail -20
pip install "flashinfer==0.1.6+cu121torch2.3" --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ --force-reinstall --no-deps 2>&1 | tail -5

# 验证安装
python -c "from sarathi import pos_encoding_ops; print('✅ sarathi C++ extensions loaded')"

cd /users/7/li003385/workspace/Sai_speculative_vidur
pip install -e . -q
echo "✅ Vidur installed"

# 运行 MLP Profiling
echo ""
echo "运行 MLP Profiling..."
export MODEL_NAME="$MODEL_NAME"
export DEVICE="v100"
export PYTHONPATH="/users/7/li003385/workspace/sarathi-serve:${PYTHONPATH:-}"

# 创建临时 profiling 输出目录
TEMP_OUTPUT="profiling_outputs_v100_$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "$TEMP_OUTPUT/mlp"

python -m vidur.profiling.mlp.main \
    --models "$MODEL_NAME" \
    --num_gpus 1 \
    --num_tensor_parallel_workers 1 \
    --max_tokens 4096 \
    --output_dir "$TEMP_OUTPUT/mlp" 2>&1 | tee mlp_profiling.log

# 检查 MLP 结果
MLP_CSV=$(find "$TEMP_OUTPUT/mlp" -name "mlp.csv" | head -1)
if [ -f "$MLP_CSV" ]; then
    echo "✅ MLP profiling completed"
    cp "$MLP_CSV" "$OUTPUT_DIR/mlp.csv"
    echo "MLP data lines: $(wc -l < "$OUTPUT_DIR/mlp.csv")"
else
    echo "❌ MLP profiling failed"
    exit 1
fi

echo ""
echo "========================================"
echo "Step 2: Attention Profiling (PyTorch Native)"
echo "========================================"

python profile_attention_v100.py \
    --model "$MODEL_NAME" \
    --n_embd $N_EMBD \
    --n_q_head $N_Q_HEAD \
    --n_kv_head $N_KV_HEAD \
    --output_dir "$OUTPUT_DIR" 2>&1 | tee attention_profiling.log

# 检查 Attention 结果
if [ -f "$OUTPUT_DIR/meta-llama-Llama-3.2-1B-Instruct/attention.csv" ]; then
    echo "✅ Attention profiling completed"
    mv "$OUTPUT_DIR/meta-llama-Llama-3.2-1B-Instruct/attention.csv" "$OUTPUT_DIR/attention.csv"
    rmdir "$OUTPUT_DIR/meta-llama-Llama-3.2-1B-Instruct" 2>/dev/null || true
    echo "Attention data lines: $(wc -l < "$OUTPUT_DIR/attention.csv")"
else
    echo "❌ Attention profiling failed"
    exit 1
fi

echo ""
echo "========================================"
echo "Profiling Summary"
echo "========================================"
echo ""
echo "Model: $MODEL_NAME"
echo "GPU: V100"
echo "Data Location: $OUTPUT_DIR"
echo ""
echo "Results:"
ls -lh "$OUTPUT_DIR"/*.csv
echo ""
echo "✅ MLP profiling: $(wc -l < "$OUTPUT_DIR/mlp.csv") lines"
echo "✅ Attention profiling (PyTorch Native): $(wc -l < "$OUTPUT_DIR/attention.csv") lines"
echo ""
echo "========================================"
echo "✅ V100 PROFILING COMPLETE"
echo "========================================"
echo ""
echo "Job completed at: $(date)"

