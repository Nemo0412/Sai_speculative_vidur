# 🎉 从这里开始 - Auto Profiling 工具

## 👋 欢迎！

恭喜！你现在拥有了一套完整的自动化 profiling 工具。这个工具可以帮助你快速为任何新模型在当前设备上进行 profiling，让 Vidur 模拟器能够准确模拟该模型的推理性能。

---

## ⚡ 5 秒快速开始

```bash
./quick_profile.sh Qwen/Qwen-7B
```

就这么简单！✨

---

## 📦 你获得了什么？

### 🔧 3 个强大的脚本

1. **`auto_profile.py`** - Python 自动化 profiling 脚本
   - 自动检测 GPU 类型（A100/H100/A40）
   - 自动检查和添加模型配置
   - 自动运行 MLP + Attention profiling
   - 自动保存结果到正确位置

2. **`quick_profile.sh`** - 一键快速启动脚本
   - 自动激活虚拟环境
   - 自动启动 Ray
   - 一行命令完成所有操作

3. **`test_auto_profile_config.py`** - 配置验证脚本
   - 验证所有配置是否正确
   - 检查模型配置完整性

### 📚 6 个详尽的文档

1. **[PROFILING_README.md](PROFILING_README.md)** - 快速开始指南 ⭐ 推荐首读
2. **[AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md)** - 详细使用指南
3. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 命令速查表
4. **[AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md)** - 功能总结
5. **[AUTO_PROFILING_COMPLETE.md](AUTO_PROFILING_COMPLETE.md)** - 完成总结
6. **[DOCS_INDEX.md](DOCS_INDEX.md)** - 文档导航索引

### ✅ 示例配置

- **Qwen-7B** 配置已添加到 `model_configs.yaml`
- 可直接用于 profiling 和模拟

---

## 🚀 三种使用方式

### 方式 1: 一键快速（最简单）

```bash
./quick_profile.sh Qwen/Qwen-7B
```

### 方式 2: Python 脚本（更灵活）

```bash
python auto_profile.py --model Qwen/Qwen-7B
```

### 方式 3: 完整流程（最详细）

```bash
# 1. 环境准备
source .venv/bin/activate
ray start --head

# 2. 运行 profiling
python auto_profile.py --model Qwen/Qwen-7B

# 3. 验证结果
ls -la data/profiling/compute/a100/Qwen/Qwen-7B/

# 4. 运行模拟
python run.py prefill Qwen/Qwen-7B A100 --batch_size 2 --sequence_length 128
```

---

## 📖 建议阅读顺序

### 🎯 如果你是新手

1. **阅读这个文件（2 分钟）** ← 你在这里
2. **阅读 [PROFILING_README.md](PROFILING_README.md)（5 分钟）** - 快速了解
3. **运行 `./quick_profile.sh Qwen/Qwen-7B`** - 实际操作
4. **查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)（3 分钟）** - 记住常用命令

**总时间：10 分钟上手**

### 🔍 如果你想深入了解

1. **阅读 [PROFILING_README.md](PROFILING_README.md)** - 快速概览
2. **阅读 [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md)** - 详细学习
3. **阅读 [AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md)** - 技术细节

**总时间：30 分钟深入学习**

### 🛠️ 如果你是开发者

1. **阅读 [AUTO_PROFILING_COMPLETE.md](AUTO_PROFILING_COMPLETE.md)** - 整体架构
2. **查看源代码** - `auto_profile.py`, `quick_profile.sh`
3. **阅读 [docs/profiling.md](docs/profiling.md)** - 原始文档

**总时间：60 分钟全面掌握**

---

## ✅ 验证安装

运行这个命令检查一切是否就绪：

```bash
python test_auto_profile_config.py
```

**预期输出：**
```
✅ All tests passed!
🎉 Your auto profiling setup is ready to use!
```

---

## 📊 工作流程

### 完整的 Profiling 流程

```
1. 检测 GPU
   ↓
2. 检查模型配置
   ↓
3. MLP Profiling
   ↓
4. Attention Profiling
   ↓
5. 保存结果
   ↓
6. 开始模拟！
```

### 时间估算

- **环境准备**: 1 分钟
- **Profiling 运行**: 15-50 分钟（取决于 GPU 数量）
- **结果验证**: 1 分钟

**总时间**: 约 20-60 分钟（其中大部分时间是自动运行）

---

## 🎯 实际示例

### 示例 1: Profile Qwen-7B

```bash
# 最简单的方式
./quick_profile.sh Qwen/Qwen-7B

# 等待完成...
# ✅ Profiling Complete!
# 📁 Profiling data saved to: data/profiling/compute/a100/Qwen/Qwen-7B

# 运行模拟测试
python run.py prefill Qwen/Qwen-7B A100 --batch_size 2 --sequence_length 128
```

### 示例 2: 自定义配置

```bash
python auto_profile.py \
  --model Qwen/Qwen-7B \
  --num_gpus 4 \
  --tensor_parallel 1,2,4 \
  --max_tokens 8192
```

### 示例 3: 添加新模型

```bash
# 1. 编辑配置文件
vim model_configs.yaml
# 添加你的模型配置

# 2. 运行 profiling
python auto_profile.py --model your-org/your-model

# 3. 开始使用！
python run.py prefill your-org/your-model A100 --batch_size 2 --sequence_length 128
```

---

## 🔧 前置要求

### 必需

- ✅ GPU 机器（A100/H100/A40）
- ✅ NVIDIA 驱动和 `nvidia-smi`
- ✅ Python 虚拟环境
- ✅ Ray（用于并行 profiling）

### 环境设置

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 启动 Ray
ray start --head

# 3. 验证 GPU
nvidia-smi
```

---

## 📁 文件位置

```
Sai_speculative_vidur/
│
├── START_HERE.md                    # 👈 本文档（从这里开始）
│
├── 🔧 核心脚本
│   ├── auto_profile.py              # Python 自动化脚本
│   ├── quick_profile.sh             # Shell 快速脚本
│   └── test_auto_profile_config.py  # 配置测试脚本
│
├── 📚 文档
│   ├── PROFILING_README.md          # ⭐ 快速开始（推荐首读）
│   ├── AUTO_PROFILING_GUIDE.md      # 详细指南
│   ├── QUICK_REFERENCE.md           # 命令速查表
│   ├── AUTO_PROFILING_SUMMARY.md    # 功能总结
│   ├── AUTO_PROFILING_COMPLETE.md   # 完成总结
│   └── DOCS_INDEX.md                # 文档索引
│
├── ⚙️ 配置
│   └── model_configs.yaml           # 模型配置（已添加 Qwen-7B）
│
└── 📁 数据目录
    └── data/profiling/compute/
        ├── a100/                    # A100 profiling 数据
        ├── h100/                    # H100 profiling 数据
        └── a40/                     # A40 profiling 数据
```

---

## 🐛 常见问题

### Q: nvidia-smi 未找到？
**A**: 确保在有 GPU 的机器上运行，检查 NVIDIA 驱动

### Q: Ray 连接错误？
**A**: 运行 `ray start --head`

### Q: 模型配置不存在？
**A**: 脚本会提示添加，或手动编辑 `model_configs.yaml`

### Q: GPU 内存不足？
**A**: 减少 `--num_gpus` 或 `--max_tokens` 参数

### Q: 找不到某个命令？
**A**: 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 快速参考

---

## 💡 小贴士

1. **首次 profiling 需要时间** - 请耐心等待（15-50 分钟）
2. **使用更多 GPU 可以加速** - `--num_gpus 4` 或 `8`
3. **结果可以重复使用** - 同一模型-设备组合只需 profile 一次
4. **配置很重要** - 确保模型配置准确
5. **遇到问题看文档** - 所有文档都有详细的故障排除

---

## 🎉 下一步

### 立即开始

```bash
# 最快的方式
./quick_profile.sh Qwen/Qwen-7B
```

### 学习更多

- 📖 阅读 [PROFILING_README.md](PROFILING_README.md)
- 🔍 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- 📚 浏览 [DOCS_INDEX.md](DOCS_INDEX.md)

### 获取帮助

```bash
# 查看帮助
python auto_profile.py --help

# 测试配置
python test_auto_profile_config.py

# 查看文档
cat PROFILING_README.md
```

---

## 📞 支持

### 命令行帮助

```bash
python auto_profile.py --help
```

### 文档导航

需要特定信息？查看 [DOCS_INDEX.md](DOCS_INDEX.md) 快速找到你需要的文档

### 配置验证

```bash
python test_auto_profile_config.py
```

---

## 🏆 你已准备就绪！

现在你拥有：

- ✅ 强大的自动化工具
- ✅ 完整的文档系统
- ✅ 示例配置和代码
- ✅ 验证和测试工具

### 开始使用

```bash
./quick_profile.sh Qwen/Qwen-7B
```

---

**祝你 Profiling 顺利，模拟成功！** 🚀

---

_如有问题，请查看文档或运行测试脚本_

**文档索引**: [DOCS_INDEX.md](DOCS_INDEX.md)  
**快速参考**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)  
**详细指南**: [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md)

