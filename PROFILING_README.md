# 🚀 如何 Profiling 新模型

## 三步完成 Profiling

### 1. 修改模型名称
```bash
vim profiling.sh
```
修改第 17 行：
```bash
MODEL_NAME="Qwen/Qwen-7B"  # 改成你的模型
```

### 2. 提交作业
```bash
sbatch profiling_job.sh
```

### 3. 监控进度
```bash
tail -f logs/profiling_*.out
```

看到 **SUCCESS!** 就完成了！

---

## 输出位置

数据自动保存在：
```
data/profiling/compute/{gpu_type}/{org}/{model}/
├── mlp.csv
└── attention.csv
```

例如：`data/profiling/compute/a100/Qwen/Qwen-7B/`

---

## 常用命令

```bash
# 查看作业状态
squeue -u $USER

# 查看最新日志
tail -30 logs/profiling_*.out

# 检查数据
ls -lh data/profiling/compute/a100/Qwen/Qwen-7B/
```

---

## 完整示例

```bash
# 1. 改模型
vim profiling.sh
# MODEL_NAME="meta-llama/Llama-2-7b-hf"

# 2. (可选) 改 GPU 类型
vim profiling_job.sh
# #SBATCH --gres=gpu:h100:1

# 3. 提交
sbatch profiling_job.sh

# 4. 监控
tail -f logs/profiling_*.out

# 5. 使用
python3 run.py prefill Qwen/Qwen-7B A100 --batch_size 4 --sequence_length 256
```

---

**就这么简单！** 🎉
