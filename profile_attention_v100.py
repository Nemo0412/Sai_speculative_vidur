#!/usr/bin/env python3
"""
V100-compatible Attention Profiling Script
使用 PyTorch native attention 替代 flashinfer
"""

import argparse
import csv
import math
import os
import time
from dataclasses import dataclass
from typing import Tuple

import torch
import torch.nn.functional as F


@dataclass
class AttentionConfig:
    """Attention 配置"""
    n_embd: int
    n_q_head: int
    n_kv_head: int
    block_size: int = 16
    max_model_len: int = 4096


def scaled_dot_product_attention_v100(
    query: torch.Tensor,  # [batch_size, n_q_heads, seq_len, head_dim]
    key: torch.Tensor,    # [batch_size, n_kv_heads, seq_len, head_dim]
    value: torch.Tensor,  # [batch_size, n_kv_heads, seq_len, head_dim]
    scale: float,
    n_q_heads: int,
    n_kv_heads: int,
) -> torch.Tensor:
    """V100-compatible scaled dot product attention with GQA support"""
    
    # Handle Grouped Query Attention (GQA)
    if n_q_heads != n_kv_heads:
        # Repeat KV heads to match Q heads
        n_groups = n_q_heads // n_kv_heads
        # key: [batch, n_kv_heads, seq, head_dim] -> [batch, n_q_heads, seq, head_dim]
        key = key.repeat_interleave(n_groups, dim=1)
        value = value.repeat_interleave(n_groups, dim=1)
    
    # Q @ K^T
    attn_weights = torch.matmul(query, key.transpose(-2, -1)) * scale
    
    # Softmax
    attn_weights = F.softmax(attn_weights, dim=-1)
    
    # @ V
    output = torch.matmul(attn_weights, value)
    
    return output


def profile_attention_decode(
    config: AttentionConfig,
    batch_size: int,
    kv_cache_size: int,
    num_iterations: int = 10,
    warmup_iterations: int = 2,
) -> float:
    """Profile decode attention (single token generation)"""
    
    device = torch.device('cuda')
    dtype = torch.float16
    
    head_dim = config.n_embd // config.n_q_head
    scale = 1.0 / math.sqrt(head_dim)
    
    # 创建输入张量 (decode: seq_len=1)
    query = torch.randn(
        batch_size, config.n_q_head, 1, head_dim,
        device=device, dtype=dtype
    )
    
    # KV cache
    key_cache = torch.randn(
        batch_size, config.n_kv_head, kv_cache_size, head_dim,
        device=device, dtype=dtype
    )
    value_cache = torch.randn(
        batch_size, config.n_kv_head, kv_cache_size, head_dim,
        device=device, dtype=dtype
    )
    
    # Warmup
    for _ in range(warmup_iterations):
        _ = scaled_dot_product_attention_v100(
            query, key_cache, value_cache, scale,
            config.n_q_head, config.n_kv_head
        )
        torch.cuda.synchronize()
    
    # Profiling
    torch.cuda.synchronize()
    start = time.time()
    
    for _ in range(num_iterations):
        _ = scaled_dot_product_attention_v100(
            query, key_cache, value_cache, scale,
            config.n_q_head, config.n_kv_head
        )
    
    torch.cuda.synchronize()
    end = time.time()
    
    avg_time = (end - start) / num_iterations
    return avg_time * 1000  # 转换为毫秒


def profile_attention_prefill(
    config: AttentionConfig,
    batch_size: int,
    prefill_chunk_size: int,
    kv_cache_size: int,
    num_iterations: int = 10,
    warmup_iterations: int = 2,
) -> float:
    """Profile prefill attention"""
    
    device = torch.device('cuda')
    dtype = torch.float16
    
    head_dim = config.n_embd // config.n_q_head
    scale = 1.0 / math.sqrt(head_dim)
    
    # 创建输入张量 (prefill: seq_len=prefill_chunk_size)
    query = torch.randn(
        batch_size, config.n_q_head, prefill_chunk_size, head_dim,
        device=device, dtype=dtype
    )
    key = torch.randn(
        batch_size, config.n_kv_head, prefill_chunk_size, head_dim,
        device=device, dtype=dtype
    )
    value = torch.randn(
        batch_size, config.n_kv_head, prefill_chunk_size, head_dim,
        device=device, dtype=dtype
    )
    
    # Warmup
    for _ in range(warmup_iterations):
        _ = scaled_dot_product_attention_v100(
            query, key, value, scale,
            config.n_q_head, config.n_kv_head
        )
        torch.cuda.synchronize()
    
    # Profiling
    torch.cuda.synchronize()
    start = time.time()
    
    for _ in range(num_iterations):
        _ = scaled_dot_product_attention_v100(
            query, key, value, scale,
            config.n_q_head, config.n_kv_head
        )
    
    torch.cuda.synchronize()
    end = time.time()
    
    avg_time = (end - start) / num_iterations
    return avg_time * 1000  # 转换为毫秒


def generate_profiling_data(
    config: AttentionConfig,
    output_file: str,
):
    """生成完整的 attention profiling 数据"""
    
    print(f"开始 Attention Profiling...")
    print(f"  模型配置: n_embd={config.n_embd}, n_q_head={config.n_q_head}, n_kv_head={config.n_kv_head}")
    print(f"  输出文件: {output_file}")
    
    results = []
    
    # 定义测试参数组合
    batch_sizes = [1, 2, 4, 8, 16, 32, 64, 128]
    prefill_chunk_sizes = [64, 128, 256, 512, 1024, 2048]
    kv_cache_sizes = [0, 64, 128, 256, 512, 1024, 2048, 4096]
    
    total_combinations = len(batch_sizes) * (len(prefill_chunk_sizes) + len(kv_cache_sizes))
    completed = 0
    
    # Prefill profiling
    print("\n🔵 Prefill Profiling...")
    for batch_size in batch_sizes:
        for prefill_chunk_size in prefill_chunk_sizes:
            try:
                latency = profile_attention_prefill(
                    config, batch_size, prefill_chunk_size, 0
                )
                
                results.append({
                    'time_stats.attn_input_reshape.min': 0.0,
                    'time_stats.attn_input_reshape.max': 0.0,
                    'time_stats.attn_input_reshape.mean': 0.0,
                    'time_stats.attn_input_reshape.median': 0.0,
                    'time_stats.attn_input_reshape.std': 0.0,
                    'time_stats.attn_kv_cache_save.min': 0.0,
                    'time_stats.attn_kv_cache_save.max': 0.0,
                    'time_stats.attn_kv_cache_save.mean': 0.0,
                    'time_stats.attn_kv_cache_save.median': 0.0,
                    'time_stats.attn_kv_cache_save.std': 0.0,
                    'time_stats.attn_prefill.min': latency,
                    'time_stats.attn_prefill.max': latency,
                    'time_stats.attn_prefill.mean': latency,
                    'time_stats.attn_prefill.median': latency,
                    'time_stats.attn_prefill.std': 0.0,
                    'time_stats.attn_decode.min': 0.0,
                    'time_stats.attn_decode.max': 0.0,
                    'time_stats.attn_decode.mean': 0.0,
                    'time_stats.attn_decode.median': 0.0,
                    'time_stats.attn_decode.std': 0.0,
                    'time_stats.attn_output_reshape.min': 0.0,
                    'time_stats.attn_output_reshape.max': 0.0,
                    'time_stats.attn_output_reshape.mean': 0.0,
                    'time_stats.attn_output_reshape.median': 0.0,
                    'time_stats.attn_output_reshape.std': 0.0,
                    'n_embd': config.n_embd,
                    'n_q_head': config.n_q_head,
                    'n_kv_head': config.n_kv_head,
                    'block_size': config.block_size,
                    'num_tensor_parallel_workers': 1,
                    'max_model_len': config.max_model_len,
                    'batch_size': batch_size,
                    'prefill_chunk_size': prefill_chunk_size,
                    'kv_cache_size': 0,
                    'is_prefill': True,
                    'attention_backend': 'AttentionBackend.PYTORCH_NATIVE',
                })
                
                completed += 1
                if completed % 10 == 0:
                    print(f"  进度: {completed}/{total_combinations} ({100*completed/total_combinations:.1f}%)")
                    
            except RuntimeError as e:
                print(f"  跳过 batch_size={batch_size}, prefill={prefill_chunk_size}: {e}")
    
    # Decode profiling
    print("\n🟢 Decode Profiling...")
    for batch_size in batch_sizes:
        for kv_cache_size in kv_cache_sizes:
            if kv_cache_size == 0:
                continue
            
            try:
                latency = profile_attention_decode(
                    config, batch_size, kv_cache_size
                )
                
                results.append({
                    'time_stats.attn_input_reshape.min': 0.0,
                    'time_stats.attn_input_reshape.max': 0.0,
                    'time_stats.attn_input_reshape.mean': 0.0,
                    'time_stats.attn_input_reshape.median': 0.0,
                    'time_stats.attn_input_reshape.std': 0.0,
                    'time_stats.attn_kv_cache_save.min': 0.0,
                    'time_stats.attn_kv_cache_save.max': 0.0,
                    'time_stats.attn_kv_cache_save.mean': 0.0,
                    'time_stats.attn_kv_cache_save.median': 0.0,
                    'time_stats.attn_kv_cache_save.std': 0.0,
                    'time_stats.attn_prefill.min': 0.0,
                    'time_stats.attn_prefill.max': 0.0,
                    'time_stats.attn_prefill.mean': 0.0,
                    'time_stats.attn_prefill.median': 0.0,
                    'time_stats.attn_prefill.std': 0.0,
                    'time_stats.attn_decode.min': latency,
                    'time_stats.attn_decode.max': latency,
                    'time_stats.attn_decode.mean': latency,
                    'time_stats.attn_decode.median': latency,
                    'time_stats.attn_decode.std': 0.0,
                    'time_stats.attn_output_reshape.min': 0.0,
                    'time_stats.attn_output_reshape.max': 0.0,
                    'time_stats.attn_output_reshape.mean': 0.0,
                    'time_stats.attn_output_reshape.median': 0.0,
                    'time_stats.attn_output_reshape.std': 0.0,
                    'n_embd': config.n_embd,
                    'n_q_head': config.n_q_head,
                    'n_kv_head': config.n_kv_head,
                    'block_size': config.block_size,
                    'num_tensor_parallel_workers': 1,
                    'max_model_len': config.max_model_len,
                    'batch_size': batch_size,
                    'prefill_chunk_size': 0,
                    'kv_cache_size': kv_cache_size,
                    'is_prefill': False,
                    'attention_backend': 'AttentionBackend.PYTORCH_NATIVE',
                })
                
                completed += 1
                if completed % 10 == 0:
                    print(f"  进度: {completed}/{total_combinations} ({100*completed/total_combinations:.1f}%)")
                    
            except RuntimeError as e:
                print(f"  跳过 batch_size={batch_size}, kv_cache={kv_cache_size}: {e}")
    
    # 保存结果
    print(f"\n💾 保存结果到 {output_file}...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"✅ 完成！生成了 {len(results)} 行数据")


def main():
    parser = argparse.ArgumentParser(description="V100 Attention Profiling")
    parser.add_argument("--model", type=str, required=True, help="Model name")
    parser.add_argument("--n_embd", type=int, required=True, help="Embedding dimension")
    parser.add_argument("--n_q_head", type=int, required=True, help="Number of Q heads")
    parser.add_argument("--n_kv_head", type=int, required=True, help="Number of KV heads")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory")
    
    args = parser.parse_args()
    
    # 创建配置
    config = AttentionConfig(
        n_embd=args.n_embd,
        n_q_head=args.n_q_head,
        n_kv_head=args.n_kv_head,
    )
    
    # 生成输出文件路径
    model_dir = args.model.replace('/', '-')
    output_file = os.path.join(args.output_dir, model_dir, "attention.csv")
    
    # 运行 profiling
    generate_profiling_data(config, output_file)


if __name__ == "__main__":
    main()

