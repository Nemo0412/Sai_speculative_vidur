#!/bin/bash
#SBATCH --job-name=profiling
#SBATCH --partition=interactive-gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=03:00:00
#SBATCH --output=logs/profiling_%j.out
#SBATCH --error=logs/profiling_%j.err

################################################################################
# SLURM Job Wrapper for profiling.sh
################################################################################
# 使用方法：
#   1. 在 profiling.sh 中修改 MODEL_NAME
#   2. 运行: sbatch profiling_job.sh
#
# 注意：如果需要使用不同的 GPU，修改上面的 #SBATCH --gres 行：
#   - A100: --gres=gpu:a100:1
#   - H100: --gres=gpu:h100:1
#   - A40:  --gres=gpu:a40:1
################################################################################

# 创建 logs 目录
mkdir -p logs

# 加载 CUDA 模块
module load cuda/12.1.1

# 加载更新的 GCC (sarathi C++ 扩展需要 GCC 9+)
echo "Loading GCC 11.3.0 for C++ compilation..."
module load gcc/11.3.0
gcc --version

# 初始化 conda (在其他模块加载之前/之后立即初始化)
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
echo "Model Profiling Job"
echo "Job ID: $SLURM_JOB_ID"
echo "Started at: $(date)"
echo "Running on node: $(hostname)"
echo "========================================"
echo ""

# 切换到工作目录
cd /users/7/li003385/workspace/Sai_speculative_vidur

# 创建或激活 conda 环境
echo "========================================"
echo "Setting up Conda Environment"
echo "========================================"
if ! conda env list | grep -q "^vidur "; then
    echo "Creating vidur conda environment..."
    conda env create -f environment.yaml -y
else
    echo "Vidur environment already exists"
fi

echo "Activating vidur environment..."
conda activate vidur

echo "Python version:"
python --version
echo "Python location:"
which python
echo "Pip location:"
which pip
echo "Conda environment:"
echo $CONDA_DEFAULT_ENV
echo ""

# 安装 sarathi-serve（如果需要）
echo "========================================"
echo "Installing sarathi-serve"
echo "========================================"
cd /users/7/li003385/workspace

if [ ! -d "sarathi-serve" ]; then
    echo "Cloning sarathi-serve..."
    git clone https://github.com/microsoft/sarathi-serve
    cd sarathi-serve
    echo "Checking out vidur branch..."
    git checkout vidur
else
    cd sarathi-serve
    echo "sarathi-serve already cloned, pulling latest..."
    git checkout vidur
    git pull origin vidur || true
fi

echo ""
echo "Installing sarathi-serve package..."

# 修改 setup.py 以接受更新的 PyTorch 版本
if [ -f "setup.py" ]; then
    echo "Patching setup.py to accept PyTorch 2.5+..."
    # 备份原文件
    cp setup.py setup.py.bak 2>/dev/null || true
    # 修改 torch 版本要求
    sed -i 's/torch==2\.3/torch>=2.3/g' setup.py || true
    sed -i 's/torch>=2\.3,<2\.4/torch>=2.3/g' setup.py || true
fi

# 按照 sarathi-serve README 的官方安装方法
echo "Installing sarathi-serve (following official README)..."
echo "This will compile C++ extensions and install all dependencies including flashinfer..."

# 使用官方推荐的安装命令（使用 torch2.3 以匹配 vidur 分支）
# 注意：使用 --extra-index-url 而不是 -i，这样可以同时从 PyPI 和 flashinfer 仓库安装
echo "Attempting installation with torch2.3/cu121 (compatible with vidur branch)..."
MAX_JOBS=4 pip install -e . --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ 2>&1 | tee /tmp/sarathi_install.log | tail -30

# 重要：降级 flashinfer 到 0.1.6 版本（vidur 分支兼容版本）
echo "Ensuring flashinfer 0.1.6 is installed (required for vidur branch)..."
pip install "flashinfer==0.1.6+cu121torch2.3" --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ --force-reinstall --no-deps 2>&1 | tail -5

# 验证安装
echo ""
echo "Verifying sarathi-serve installation..."
INSTALL_SUCCESS=true

# 检查 C++ 扩展
if python -c "from sarathi import pos_encoding_ops; print('✅ pos_encoding_ops loaded')" 2>/dev/null; then
    echo "✅ C++ extensions compiled successfully"
else
    echo "❌ C++ extensions failed"
    INSTALL_SUCCESS=false
fi

# 检查 flashinfer
if python -c "import flashinfer; print('✅ flashinfer version:', flashinfer.__version__)" 2>/dev/null; then
    echo "✅ flashinfer installed successfully"
else
    echo "❌ flashinfer not found"
    INSTALL_SUCCESS=false
fi

# 如果第一次安装失败，尝试其他 PyTorch 版本
if [ "$INSTALL_SUCCESS" = false ]; then
    echo ""
    echo "First attempt failed, trying alternative installation..."
    MAX_JOBS=4 pip install --force-reinstall -e . --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ 2>&1 | tail -30
    
    # 确保使用正确的 flashinfer 版本
    echo "Installing flashinfer 0.1.6..."
    pip install "flashinfer==0.1.6+cu121torch2.3" --extra-index-url https://flashinfer.ai/whl/cu121/torch2.3/ --force-reinstall --no-deps 2>&1 | tail -5
    
    # 再次验证
    if python -c "from sarathi import pos_encoding_ops" 2>/dev/null && python -c "import flashinfer; assert '0.1.6' in flashinfer.__version__" 2>/dev/null; then
        echo "✅ Second attempt successful with flashinfer 0.1.6"
        INSTALL_SUCCESS=true
    fi
fi

if [ "$INSTALL_SUCCESS" = false ]; then
    echo ""
    echo "❌ sarathi-serve installation failed"
    echo "Check logs at /tmp/sarathi_install.log"
    grep -i "error" /tmp/sarathi_install.log | head -20
    exit 1
fi

# 验证并修复 sarathi 安装
echo "Verifying sarathi installation..."
python3 -c "
import sys
try:
    import sarathi
    print('✅ sarathi-serve installed successfully')
    print('   Version:', getattr(sarathi, '__version__', 'unknown'))
    print('   Location:', sarathi.__file__)
except Exception as e:
    print('❌ sarathi import failed:', e)
    print('Python path:', sys.executable)
    print('Attempting alternative installation...')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "Trying alternative installation method..."
    # 强制使用当前 Python 环境安装
    python3 -m pip install --force-reinstall --no-cache-dir --no-deps -e . 2>&1 | tail -10
    
    # 再次验证
    python3 -c "import sarathi; print('✅ Retry successful')" 2>/dev/null || {
        echo "❌ sarathi-serve installation failed completely"
        echo "Attempting to use pre-installed sarathi..."
        # 检查是否有预装的 sarathi
        python3 -c "import sys; sys.path.append('/users/7/li003385/workspace/sarathi-serve'); import sarathi; print('✅ Using pre-installed sarathi')" 2>/dev/null || exit 1
    }
fi

cd /users/7/li003385/workspace/Sai_speculative_vidur
echo ""

# 安装 Vidur
echo "========================================"
echo "Installing Vidur"
echo "========================================"
pip install -e . -q
echo "✅ Vidur installed"
echo ""

# 运行 profiling 脚本
echo "========================================"
echo "Running profiling.sh"
echo "========================================"
echo ""

./profiling.sh

# 保存退出代码
EXIT_CODE=$?

echo ""
echo "========================================"
echo "Job completed at: $(date)"
echo "Exit code: $EXIT_CODE"
echo "========================================"

exit $EXIT_CODE

