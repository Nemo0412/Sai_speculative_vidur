# 🚀 快速参考卡 - Auto Profiling

## 一键命令

```bash
# 最快开始 - 使用 Qwen-7B 示例
./quick_profile.sh Qwen/Qwen-7B
```

## 常用命令

### Profiling 相关

```bash
# Python 脚本（基本用法）
python auto_profile.py --model Qwen/Qwen-7B

# 自定义 GPU 数量
python auto_profile.py --model Qwen/Qwen-7B --num_gpus 4

# 自定义 Tensor Parallel
python auto_profile.py --model Qwen/Qwen-7B --tensor_parallel 1,2,4

# 长上下文模型
python auto_profile.py --model Qwen/Qwen-7B --max_tokens 16384

# 完整配置
python auto_profile.py \
  --model Qwen/Qwen-7B \
  --num_gpus 4 \
  --tensor_parallel 1,2,4 \
  --max_tokens 8192
```

### 环境准备

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动 Ray
ray start --head

# 检查 Ray 状态
ray status

# 停止 Ray
ray stop
```

### 配置测试

```bash
# 测试配置是否正确
python test_auto_profile_config.py

# 查看模型配置
cat model_configs.yaml | grep -A 20 "Qwen/Qwen-7B"
```

### 验证结果

```bash
# 查看 profiling 数据
ls -la data/profiling/compute/a100/Qwen/Qwen-7B/

# 查看 CSV 内容
head -20 data/profiling/compute/a100/Qwen/Qwen-7B/mlp.csv
head -20 data/profiling/compute/a100/Qwen/Qwen-7B/attention.csv
```

### 运行模拟

```bash
# Prefill 模拟
python run.py prefill Qwen/Qwen-7B A100 \
  --batch_size 2 \
  --sequence_length 128

# Decode 模拟
python run.py decode Qwen/Qwen-7B A100 \
  --batch_size 2 \
  --tokens_to_generate 4 \
  --kv_cache_length 128
```

## GPU 检测

```bash
# 查看 GPU 信息
nvidia-smi

# 只显示 GPU 名称
nvidia-smi --query-gpu=name --format=csv,noheader

# 显示 GPU 内存
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
```

## 文件位置

```bash
# 脚本
auto_profile.py              # Python 自动化脚本
quick_profile.sh             # Shell 快速脚本
test_auto_profile_config.py  # 配置测试脚本

# 配置
model_configs.yaml           # 模型配置文件

# 文档
PROFILING_README.md          # 快速开始文档
AUTO_PROFILING_GUIDE.md      # 详细使用指南
AUTO_PROFILING_SUMMARY.md    # 功能总结
QUICK_REFERENCE.md           # 本文档

# 数据
data/profiling/compute/
├── a100/                    # A100 GPU profiling 数据
├── h100/                    # H100 GPU profiling 数据
└── a40/                     # A40 GPU profiling 数据
```

## 典型工作流

### 新模型 Profiling（完整流程）

```bash
# 1. 进入项目目录
cd /users/7/li003385/workspace/Sai_speculative_vidur

# 2. 激活环境
source .venv/bin/activate

# 3. 启动 Ray
ray start --head

# 4. （可选）测试配置
python test_auto_profile_config.py

# 5. 运行 profiling
./quick_profile.sh Qwen/Qwen-7B

# 6. 验证结果
ls -la data/profiling/compute/a100/Qwen/Qwen-7B/

# 7. 测试模拟
python run.py prefill Qwen/Qwen-7B A100 --batch_size 2 --sequence_length 128
```

## 参数速查

### auto_profile.py 参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--model` | 模型名称 | **必需** | `Qwen/Qwen-7B` |
| `--num_gpus` | GPU 数量 | 自动检测 | `4` |
| `--tensor_parallel` | TP 大小（逗号分隔） | `1,2,4,8` | `1,2,4` |
| `--max_tokens` | 最大 token 数 | `4096` | `16384` |
| `--skip_config_check` | 跳过配置检查 | `False` | - |

### GPU 类型

| GPU | 标识符 | 目录 |
|-----|--------|------|
| A100 80GB | `a100` | `data/profiling/compute/a100/` |
| H100 | `h100` | `data/profiling/compute/h100/` |
| A40 | `a40` | `data/profiling/compute/a40/` |

### Tensor Parallel 配置

| GPU 配置 | 推荐 TP | 说明 |
|---------|---------|------|
| 1 GPU | `1` | 单 GPU |
| 2 GPU | `1,2` | 2 GPU TP |
| 4 GPU Pairwise | `1,2,4` | 4 GPU，部分 NVLink |
| 8 GPU DGX | `1,2,4,8` | 8 GPU，全 NVLink |

## 故障排除速查

| 问题 | 解决方案 |
|------|---------|
| `nvidia-smi: command not found` | 确保在 GPU 机器上运行 |
| `Ray not running` | 运行 `ray start --head` |
| `Model config not found` | 脚本会提示添加，或手动编辑 `model_configs.yaml` |
| `CUDA out of memory` | 减少 `--num_gpus` 或 `--max_tokens` |
| `Permission denied` | 运行 `chmod +x quick_profile.sh auto_profile.py` |

## 时间估算

| 配置 | MLP | Attention | 总时间 |
|------|-----|-----------|--------|
| 1 GPU | 15-20 min | 20-30 min | ~40-50 min |
| 4 GPU | 5-8 min | 8-12 min | ~15-20 min |
| 8 GPU | 3-5 min | 5-8 min | ~10-15 min |

## 获取帮助

```bash
# 查看 auto_profile.py 帮助
python auto_profile.py --help

# 查看 quick_profile.sh 用法
./quick_profile.sh

# 阅读文档
cat PROFILING_README.md
cat AUTO_PROFILING_GUIDE.md
```

## 示例模型配置

### Qwen-7B（已内置）

```yaml
"Qwen/Qwen-7B":
  num_layers: 32
  num_q_heads: 32
  num_kv_heads: 32
  embedding_dim: 4096
  mlp_hidden_dim: 11008
  max_position_embeddings: 8192
  use_gated_mlp: true
  use_bias: false
  use_qkv_bias: true
  activation: "silu"
  norm: "rms_norm"
  post_attn_norm: true
  vocab_size: 151936
  is_neox_style: true
  rope_theta: 10000.0
  rope_scaling: null
  partial_rotary_factor: 1.0
  no_tensor_parallel: false
```

## 完整示例

### 示例 1: 快速 Profiling

```bash
./quick_profile.sh Qwen/Qwen-7B
```

### 示例 2: 自定义配置

```bash
python auto_profile.py \
  --model Qwen/Qwen-7B \
  --num_gpus 4 \
  --tensor_parallel 1,2,4 \
  --max_tokens 8192
```

### 示例 3: 完整工作流

```bash
# 环境准备
cd /users/7/li003385/workspace/Sai_speculative_vidur
source .venv/bin/activate
ray start --head

# Profiling
python auto_profile.py --model Qwen/Qwen-7B

# 验证
ls -la data/profiling/compute/a100/Qwen/Qwen-7B/

# 模拟
python run.py prefill Qwen/Qwen-7B A100 --batch_size 2 --sequence_length 128
```

---

**提示**: 将此文档加入书签以便快速查找命令！

