#!/bin/bash

# 测试 prefill 和 decode 功能的脚本

set -e

echo "=========================================="
echo "测试 Qwen-7B on A40 的 Prefill 和 Decode"
echo "=========================================="

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

cd /users/7/li003385/workspace/Sai_speculative_vidur

# 1. 测试 Prefill
echo ""
echo "=========================================="
echo "1. 测试 Prefill"
echo "=========================================="
python3 run.py prefill Qwen/Qwen-7B A40 --batch_size 4 --sequence_length 256 --output_dir test_output_prefill

if [ $? -eq 0 ]; then
    echo "✅ Prefill 测试成功！"
else
    echo "❌ Prefill 测试失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "2. 测试 Decode"
echo "=========================================="
python3 run.py decode Qwen/Qwen-7B A40 --batch_size 8 --tokens_to_generate 4 --kv_cache_length 1024 --output_dir test_output_decode

if [ $? -eq 0 ]; then
    echo "✅ Decode 测试成功！"
else
    echo "❌ Decode 测试失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "🎉 所有测试完成！"
echo "=========================================="
echo "Prefill 结果: test_output_prefill/"
echo "Decode 结果: test_output_decode/"
echo ""
echo "SUCCESS!"

