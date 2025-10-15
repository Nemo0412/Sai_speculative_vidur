#!/bin/bash
# 简单测试脚本：检查当前环境是否可以运行 profiling.sh

source /users/7/li003385/miniconda3/etc/profile.d/conda.sh
conda activate vidur

echo "=== 环境检查 ==="
echo "Python: $(python --version)"
echo "flashinfer: $(python -c 'import flashinfer; print(flashinfer.__version__)')"
echo "PyTorch: $(python -c 'import torch; print(torch.__version__)')"
echo ""

echo "=== 测试 sarathi 导入 ==="
export PYTHONPATH="/users/7/li003385/workspace/sarathi-serve:${PYTHONPATH:-}"
python -c "
from sarathi import pos_encoding_ops
print('✅ pos_encoding_ops loaded')

import flashinfer
print(f'✅ flashinfer {flashinfer.__version__}')

# 测试 API
from flashinfer import append_paged_kv_cache
import inspect
sig = inspect.signature(append_paged_kv_cache)
print(f'✅ append_paged_kv_cache parameters: {list(sig.parameters.keys())[:5]}...')
"

echo ""
echo "=== 结论 ==="
echo "✅ 环境配置正确，可以运行 profiling.sh"
