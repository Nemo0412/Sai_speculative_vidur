# YAML Configuration System - Summary

## 概述 (Overview)

我已经成功为Vidur simulator添加了基于YAML的模型配置系统。现在你可以通过编辑YAML文件来配置模型参数，而不需要修改Python代码！

## 主要功能 (Main Features)

### 1. YAML配置文件 (`model_configs.yaml`)
- 所有模型参数都显式定义在YAML文件中
- 支持9个预配置模型（Llama-2, Llama-3, CodeLlama, InternLM, Qwen, Phi-2）
- 可以轻松添加自定义模型

### 2. 自动加载系统
- **优先级**: YAML配置 > Python硬编码配置 > 报错
- 自动从YAML加载配置（如果存在）
- 如果YAML中没有，回退到Python硬编码配置
- 完整的日志记录，显示使用哪个配置源

### 3. 简单易用
- 不需要重新编译或重启
- 修改YAML文件后直接运行即可
- 支持环境变量指定配置文件路径

## 使用方法 (How to Use)

### 添加新模型 (Add New Model)

编辑 `model_configs.yaml`:

```yaml
models:
  "my-org/my-custom-model-7b":
    num_layers: 32
    num_q_heads: 32
    num_kv_heads: 32
    embedding_dim: 4096
    mlp_hidden_dim: 11008
    max_position_embeddings: 4096
    use_gated_mlp: true
    use_bias: false
    use_qkv_bias: false
    activation: "silu"  # silu 或 gelu
    norm: "rms_norm"     # rms_norm 或 layer_norm
    post_attn_norm: true
    vocab_size: 32768
    is_neox_style: true
    rope_theta: 10000.0
    rope_scaling: null
    partial_rotary_factor: 1.0
    no_tensor_parallel: false
```

### 修改现有模型参数 (Modify Existing Model)

例如，增加Llama-2-7B的上下文长度:

```yaml
"meta-llama/Llama-2-7b-hf":
  # ... 其他参数 ...
  max_position_embeddings: 8192  # 从4096改为8192
  # ... 其他参数 ...
```

### 运行模拟 (Run Simulation)

```bash
# 使用自定义模型
python run.py prefill my-org/my-custom-model-7b A100 --batch_size 4 --sequence_length 256

# 或使用完整的simulator
python -m vidur.main --replica_config_model_name "my-org/my-custom-model-7b" --replica_config_device a100
```

## 文件说明 (Files)

| 文件 | 说明 |
|------|------|
| `model_configs.yaml` | YAML配置文件，包含所有模型参数 |
| `MODEL_CONFIG_GUIDE.md` | 完整的使用指南和文档 |
| `test_yaml_config.py` | 测试脚本，验证配置加载 |
| `vidur/config/model_config.py` | 修改后的Python代码，支持YAML加载 |

## 参数说明 (Parameters)

### 必需参数 (Required Parameters)

- `num_layers`: Transformer层数
- `num_q_heads`: Query attention头数
- `num_kv_heads`: Key-Value头数 (用于GQA)
- `embedding_dim`: 隐藏层维度
- `mlp_hidden_dim`: MLP中间层维度
- `max_position_embeddings`: 最大序列长度
- `use_gated_mlp`: 是否使用gated MLP (SwiGLU)
- `use_bias`: 是否在线性层使用bias
- `use_qkv_bias`: 是否在attention QKV使用bias
- `activation`: 激活函数 ("silu" 或 "gelu")
- `norm`: 归一化类型 ("rms_norm" 或 "layer_norm")
- `post_attn_norm`: attention后是否归一化
- `vocab_size`: 词汇表大小

### 可选参数 (Optional Parameters)

- `is_neox_style`: 是否使用GPT-NeoX风格 (默认: true)
- `rope_theta`: RoPE基础频率 (默认: 10000.0)
- `rope_scaling`: RoPE缩放配置 (默认: null)
- `partial_rotary_factor`: RoPE的维度比例 (默认: 1.0)
- `no_tensor_parallel`: 是否禁用张量并行 (默认: false)

## 测试 (Testing)

运行测试脚本验证配置:

```bash
python test_yaml_config.py
```

输出示例:
```
======================================================================
Testing YAML Model Configuration Loading
======================================================================

📦 Loading model: meta-llama/Llama-2-7b-hf
INFO Loaded 9 model configurations from model_configs.yaml
INFO Using YAML configuration for model: meta-llama/Llama-2-7b-hf
   ✅ Successfully loaded!
   └─ Layers: 32
   └─ Q Heads: 32
   └─ KV Heads: 32
   └─ Embedding Dim: 4096
   ...
```

## 优势 (Advantages)

1. **易于配置**: 不需要修改Python代码
2. **快速迭代**: 修改参数后直接运行
3. **版本控制友好**: YAML文件易于diff和merge
4. **非Python用户友好**: 不需要了解Python语法
5. **实验友好**: 轻松测试不同的模型配置
6. **文档清晰**: 所有参数都有注释说明

## 向后兼容 (Backward Compatibility)

- 完全向后兼容原有的Python硬编码配置
- 如果没有YAML文件，自动使用Python配置
- 现有代码无需修改即可继续使用

## 环境变量 (Environment Variables)

可选：指定自定义配置文件位置

```bash
export VIDUR_CONFIG_DIR=/path/to/config/directory
```

配置文件搜索顺序:
1. 项目根目录 (默认)
2. 当前工作目录
3. `VIDUR_CONFIG_DIR` 环境变量指定的目录

## 日志记录 (Logging)

系统会记录配置加载过程:

```
INFO Loaded 9 model configurations from /path/to/model_configs.yaml
INFO Using YAML configuration for model: meta-llama/Llama-2-7b-hf
INFO Creating model config for 'meta-llama/Llama-2-7b-hf' from YAML
```

## 故障排除 (Troubleshooting)

### 问题: 模型未找到
```
ValueError: [BaseModelConfig] Invalid model name: my-model
```
**解决**: 在 `model_configs.yaml` 中添加模型配置

### 问题: YAML解析错误
```
Error loading model_configs.yaml: ... Using hardcoded configs only.
```
**解决**: 检查YAML语法（缩进、引号、冒号）

### 问题: 使用了错误的配置
检查日志中的消息:
- `"Using YAML configuration..."` - 正在使用YAML ✅
- `"Using hardcoded configuration..."` - 回退到Python配置 ⚠️

## 下一步 (Next Steps)

1. 查看 `MODEL_CONFIG_GUIDE.md` 获取完整文档
2. 编辑 `model_configs.yaml` 添加你的自定义模型
3. 运行 `test_yaml_config.py` 验证配置
4. 开始使用新的配置系统！

## 示例 (Examples)

### 示例 1: 添加Mistral-7B模型

```yaml
"mistralai/Mistral-7B-v0.1":
  num_layers: 32
  num_q_heads: 32
  num_kv_heads: 8
  embedding_dim: 4096
  mlp_hidden_dim: 14336
  max_position_embeddings: 32768
  use_gated_mlp: true
  use_bias: false
  use_qkv_bias: false
  activation: "silu"
  norm: "rms_norm"
  post_attn_norm: true
  vocab_size: 32000
  is_neox_style: true
  rope_theta: 10000.0
  rope_scaling: null
  partial_rotary_factor: 1.0
  no_tensor_parallel: false
```

### 示例 2: 实验性配置

```yaml
"llama-2-7b-experimental":
  num_layers: 32
  num_q_heads: 32
  num_kv_heads: 4  # 更激进的GQA
  embedding_dim: 4096
  mlp_hidden_dim: 11008
  max_position_embeddings: 16384  # 扩展上下文
  use_gated_mlp: true
  use_bias: false
  use_qkv_bias: false
  activation: "silu"
  norm: "rms_norm"
  post_attn_norm: true
  vocab_size: 32768
  is_neox_style: true
  rope_theta: 100000.0  # 为更长上下文增加
  rope_scaling: null
  partial_rotary_factor: 1.0
  no_tensor_parallel: false
```

## 贡献 (Contributing)

如果你添加了有用的模型配置，欢迎贡献回项目！

---

**Note**: 确保在推送到GitHub时需要认证。使用 `git push` 命令推送更改。

