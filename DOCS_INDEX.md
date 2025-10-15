# 📚 文档索引 - Auto Profiling 工具

## 🎯 我想...

### 🚀 快速开始
**我想立即开始使用 → [PROFILING_README.md](PROFILING_README.md)**
- 最快的上手指南
- 一键命令
- 实际示例

### 📖 详细学习
**我想深入了解如何使用 → [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md)**
- 完整的使用说明
- 参数详解
- 故障排除
- 最佳实践

### 🔍 快速查找
**我想查找某个命令 → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)**
- 命令速查表
- 参数速查
- 故障排除速查

### 🏗️ 了解整体
**我想了解这套工具 → [AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md)**
- 功能总结
- 技术架构
- 文件清单
- 性能对比

### ✅ 验证安装
**我想检查配置是否正确 → 运行测试脚本**
```bash
python test_auto_profile_config.py
```

### 📊 了解完成情况
**我想知道都做了什么 → [AUTO_PROFILING_COMPLETE.md](AUTO_PROFILING_COMPLETE.md)**
- 完成工作总结
- 所有文件清单
- 下一步建议

---

## 📂 按文档类型浏览

### 🔧 脚本文件

| 文件 | 类型 | 用途 | 命令示例 |
|------|------|------|---------|
| `auto_profile.py` | Python | 自动化 profiling | `python auto_profile.py --model Qwen/Qwen-7B` |
| `quick_profile.sh` | Shell | 快速启动 | `./quick_profile.sh Qwen/Qwen-7B` |
| `test_auto_profile_config.py` | Python | 配置测试 | `python test_auto_profile_config.py` |

### 📚 文档文件

| 文件 | 适合人群 | 主要内容 |
|------|---------|---------|
| [PROFILING_README.md](PROFILING_README.md) | 新手、快速上手 | 工具概述、快速开始、实际示例 |
| [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md) | 需要详细说明 | 完整流程、参数详解、故障排除 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 需要查命令 | 命令速查、参数速查、示例代码 |
| [AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md) | 开发/维护者 | 功能总结、技术细节、性能对比 |
| [AUTO_PROFILING_COMPLETE.md](AUTO_PROFILING_COMPLETE.md) | 项目管理者 | 完成总结、文件清单、整体概览 |
| [DOCS_INDEX.md](DOCS_INDEX.md) | 所有人 | 文档导航、快速查找 |

### ⚙️ 配置文件

| 文件 | 用途 |
|------|------|
| `model_configs.yaml` | 模型配置（已添加 Qwen-7B） |

---

## 🎓 按学习路径浏览

### 路径 1: 快速上手（10 分钟）

```
1. PROFILING_README.md           # 5 分钟 - 了解基本概念
   ↓
2. 运行 ./quick_profile.sh       # 1 分钟 - 启动 profiling
   ↓
3. QUICK_REFERENCE.md            # 4 分钟 - 记住常用命令
```

### 路径 2: 深入学习（30 分钟）

```
1. PROFILING_README.md           # 快速概览
   ↓
2. AUTO_PROFILING_GUIDE.md       # 详细学习
   ↓
3. 实际操作 profiling            # 动手实践
   ↓
4. AUTO_PROFILING_SUMMARY.md     # 了解技术细节
```

### 路径 3: 开发维护（60 分钟）

```
1. AUTO_PROFILING_COMPLETE.md    # 整体概览
   ↓
2. AUTO_PROFILING_SUMMARY.md     # 技术架构
   ↓
3. 阅读源代码                    # auto_profile.py
   ↓
4. docs/profiling.md             # 原始文档
   ↓
5. 自定义和扩展                  # 根据需求修改
```

---

## 🔍 按问题类型查找

### 使用问题

| 问题 | 查看文档 | 章节 |
|------|---------|------|
| 如何快速开始？ | [PROFILING_README.md](PROFILING_README.md) | 快速开始 |
| 有哪些命令参数？ | [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md) | 命令行参数详解 |
| 命令忘记了怎么办？ | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 常用命令 |
| 如何添加新模型配置？ | [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md) | 准备模型配置 |

### 技术问题

| 问题 | 查看文档 | 章节 |
|------|---------|------|
| 工作原理是什么？ | [AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md) | 技术细节 |
| 目录结构是怎样的？ | [AUTO_PROFILING_COMPLETE.md](AUTO_PROFILING_COMPLETE.md) | 文件组织结构 |
| 支持哪些配置？ | [AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md) | 支持的配置 |
| 性能如何？ | [AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md) | 性能对比 |

### 故障问题

| 问题 | 查看文档 | 章节 |
|------|---------|------|
| nvidia-smi 未找到 | [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md) | 故障排除 |
| Ray 连接错误 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 故障排除速查 |
| GPU 内存不足 | [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md) | 故障排除 |
| 配置不正确 | 运行 `test_auto_profile_config.py` | - |

---

## 📊 文档特性对比

| 文档 | 长度 | 难度 | 实践性 | 详细度 |
|------|------|------|--------|--------|
| PROFILING_README.md | 中 | 低 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| AUTO_PROFILING_GUIDE.md | 长 | 中 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| QUICK_REFERENCE.md | 短 | 低 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| AUTO_PROFILING_SUMMARY.md | 长 | 中 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| AUTO_PROFILING_COMPLETE.md | 长 | 低 | ⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 推荐阅读顺序

### 👶 新手用户

1. **[PROFILING_README.md](PROFILING_README.md)** - 从这里开始
2. **运行示例** - 实际操作一次
3. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 记住常用命令

### 👨‍💻 进阶用户

1. **[PROFILING_README.md](PROFILING_README.md)** - 快速回顾
2. **[AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md)** - 深入学习
3. **[AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md)** - 技术细节

### 🔧 开发者

1. **[AUTO_PROFILING_COMPLETE.md](AUTO_PROFILING_COMPLETE.md)** - 整体了解
2. **[AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md)** - 架构设计
3. **源代码** - `auto_profile.py`, `quick_profile.sh`

---

## 🚀 快速命令

### 查看文档

```bash
# 快速开始指南
cat PROFILING_README.md

# 详细使用指南
cat AUTO_PROFILING_GUIDE.md

# 命令速查表
cat QUICK_REFERENCE.md

# 功能总结
cat AUTO_PROFILING_SUMMARY.md

# 完成总结
cat AUTO_PROFILING_COMPLETE.md
```

### 运行脚本

```bash
# 测试配置
python test_auto_profile_config.py

# 快速 profiling
./quick_profile.sh Qwen/Qwen-7B

# 自定义 profiling
python auto_profile.py --model Qwen/Qwen-7B --help
```

---

## 📞 获取帮助

### 命令行帮助

```bash
# 查看 auto_profile.py 帮助
python auto_profile.py --help

# 查看 quick_profile.sh 用法
./quick_profile.sh
```

### 文档帮助

- **快速问题** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **详细问题** → [AUTO_PROFILING_GUIDE.md](AUTO_PROFILING_GUIDE.md)
- **概念问题** → [AUTO_PROFILING_SUMMARY.md](AUTO_PROFILING_SUMMARY.md)

### 配置验证

```bash
# 运行测试脚本
python test_auto_profile_config.py
```

---

## 🔗 相关项目文档

### Vidur 项目文档

| 文档 | 用途 |
|------|------|
| [README.md](README.md) | 项目主文档 |
| [HOW_TO_USE.md](HOW_TO_USE.md) | 模拟器使用指南 |
| [MODEL_CONFIG_GUIDE.md](MODEL_CONFIG_GUIDE.md) | 模型配置指南 |
| [docs/profiling.md](docs/profiling.md) | 原始 profiling 文档 |
| [docs/metrics.md](docs/metrics.md) | 指标说明 |

### 配置文件

| 文件 | 用途 |
|------|------|
| `model_configs.yaml` | 模型配置 |
| `environment.yml` | Conda 环境配置 |
| `requirements.txt` | Python 依赖 |

---

## 📝 文档版本

- **当前版本**: v1.0
- **最后更新**: 2024
- **维护者**: AI Assistant

---

## 🎉 快速开始

**不确定从哪里开始？** 

👉 **建议：先阅读 [PROFILING_README.md](PROFILING_README.md)，然后运行：**

```bash
./quick_profile.sh Qwen/Qwen-7B
```

**遇到问题？**

👉 **查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 的故障排除章节**

---

**祝你使用愉快！** 🚀

