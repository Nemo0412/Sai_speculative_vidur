# Vidur Simulator - 快速使用指南

## 📦 已完成的功能

✅ **简化运行脚本** - 一键运行prefill和decode模拟  
✅ **YAML配置系统** - 无需修改代码即可配置模型  
✅ **自定义模型支持** - 添加了 `leshu/leshu_test_model` 示例  
✅ **自动结果显示** - 直接输出Prefill/Decode latency  
✅ **完整文档** - 中英文文档齐全  

## 🚀 立即开始

### 1. 环境准备（如果还没做）

```bash
cd /home/li003385/workspace/vidur
source .venv/bin/activate
```

### 2. 快速测试命令

#### 测试1: 验证模型加载 ⚡（几秒钟）
```bash
python -c "from vidur.config.model_config import BaseModelConfig; config = BaseModelConfig.create_from_name('leshu/leshu_test_model'); print('✅ 成功加载模型:', config.get_name())"
```

**预期输出:**
```
INFO Loaded 10 model configurations from model_configs.yaml
INFO Using YAML configuration for model: leshu/leshu_test_model
✅ 成功加载模型: leshu/leshu_test_model
```

#### 测试2: 运行Prefill模拟 🔵（2-5分钟）
```bash
python run.py prefill leshu/leshu_test_model A100 --batch_size 2 --sequence_length 128
```

**预期输出:**
```
============================================================
📊 SIMULATION RESULTS - LATENCY METRICS
============================================================

🔵 PREFILL LATENCY (seconds):
   Mean:    0.018706s
   Median:  0.018706s
   Min:     0.013315s
   Max:     0.024097s
   ...
```

#### 测试3: 运行Decode模拟 🟢（2-5分钟）
```bash
python run.py decode leshu/leshu_test_model A100 --batch_size 2 --tokens_to_generate 4 --kv_cache_length 128
```

**预期输出:**
```
🟢 DECODE LATENCY (seconds):
   Mean:    0.008063s
   Median:  0.008063s
   ...
```

## 📝 推送到GitHub

### 方法1: 使用脚本（推荐）

```bash
./push.sh
```

### 方法2: 手动推送

```bash
git push origin Sai_speculative_decode
```

如果遇到认证问题，查看 `PUSH_TO_GITHUB.md` 获取详细说明。

## 📚 完整文档

- `README.md` - 项目主文档  
- `MODEL_CONFIG_GUIDE.md` - 配置指南（英文）  
- `YAML_CONFIG_SUMMARY.md` - 配置总结（中文）  
- `FINAL_SUMMARY.md` - 功能完整总结  
- `PUSH_TO_GITHUB.md` - GitHub推送详细说明  

## 🎯 添加你自己的模型

### 步骤1: 编辑配置文件

```bash
vim model_configs.yaml  # 或使用你喜欢的编辑器
```

添加你的模型配置:

```yaml
models:
  "your-org/your-model-name":
    num_layers: 32
    num_q_heads: 32
    num_kv_heads: 8
    embedding_dim: 4096
    mlp_hidden_dim: 11008
    max_position_embeddings: 4096
    use_gated_mlp: true
    use_bias: false
    use_qkv_bias: false
    activation: "silu"
    norm: "rms_norm"
    post_attn_norm: true
    vocab_size: 32768
    is_neox_style: true
    rope_theta: 10000.0
    rope_scaling: null
    partial_rotary_factor: 1.0
    no_tensor_parallel: false
```

### 步骤2: 运行模拟

```bash
python run.py prefill your-org/your-model-name A100 --batch_size 4 --sequence_length 256
```

## ⚙️ 可用的模型

通过YAML配置的模型（10个）:
- `meta-llama/Llama-2-7b-hf`
- `meta-llama/Llama-2-70b-hf`
- `meta-llama/Meta-Llama-3-8B`
- `meta-llama/Meta-Llama-3-70B`
- `codellama/CodeLlama-34b-Instruct-hf`
- `internlm/internlm-20b`
- `internlm/internlm2-20b`
- `Qwen/Qwen-72B`
- `microsoft/phi-2`
- `leshu/leshu_test_model` ⭐（新增示例）

## 🔍 故障排除

### 问题1: 模型加载失败
```
ValueError: [BaseModelConfig] Invalid model name: xxx
```
**解决**: 检查模型名称是否在 `model_configs.yaml` 中，或者拼写是否正确。

### 问题2: Simulation运行很慢
**原因**: 第一次运行需要训练机器学习模型，大约需要2-5分钟。  
**解决**: 等待完成，后续运行会使用缓存，速度会快很多。

### 问题3: GitHub推送需要认证
**解决**: 
1. 创建Personal Access Token (推荐)
2. 或配置SSH密钥
详见 `PUSH_TO_GITHUB.md`

## 💡 使用技巧

1. **快速测试**: 使用小的batch_size和sequence_length进行快速验证
2. **缓存利用**: 第一次运行后，模型会被缓存，后续运行更快
3. **配置实验**: 直接修改YAML文件测试不同配置
4. **日志查看**: 注意INFO日志了解配置加载源（YAML vs 硬编码）

## 📊 性能参数说明

- `batch_size`: 同时处理的请求数量（建议: 1-8）
- `sequence_length`: 输入prompt长度（prefill）
- `tokens_to_generate`: 生成的token数量（decode）
- `kv_cache_length`: KV缓存长度（decode，通常等于sequence_length）

## 🎉 完成！

现在你可以:
1. ✅ 运行现有模型的模拟
2. ✅ 添加自定义模型配置
3. ✅ 获取prefill和decode的latency结果
4. ✅ 实验不同的模型配置

需要更多帮助？查看完整文档或运行:
```bash
python run.py --help
```

---

**祝使用愉快！** 🚀

