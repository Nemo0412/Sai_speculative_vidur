#!/usr/bin/env python3
"""
Auto Profiling Script for Vidur Simulator
==========================================

This script automates the profiling process for new models on the current device.
It performs MLP and Attention profiling, and automatically places the results in the correct directory.

Usage:
    python auto_profile.py --model Qwen/Qwen-7B
    python auto_profile.py --model Qwen/Qwen-7B --num_gpus 4 --tensor_parallel 1,2,4
"""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
import yaml
from pathlib import Path


def get_gpu_info():
    """Detect the current GPU type and count."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            check=True
        )
        
        gpu_lines = result.stdout.strip().split('\n')
        if not gpu_lines:
            raise RuntimeError("No GPUs detected")
        
        first_gpu = gpu_lines[0].strip()
        gpu_count = len(gpu_lines)
        
        # Determine GPU type based on name
        if 'A100' in first_gpu:
            gpu_type = 'a100'
        elif 'H100' in first_gpu:
            gpu_type = 'h100'
        elif 'A40' in first_gpu:
            gpu_type = 'a40'
        else:
            # Default to a100 or ask user
            print(f"⚠️  Unknown GPU type: {first_gpu}")
            print("Please specify the GPU type manually (a100/h100/a40):")
            gpu_type = input().strip().lower()
        
        return gpu_type, gpu_count, first_gpu
    
    except FileNotFoundError:
        print("❌ nvidia-smi not found. Please ensure NVIDIA drivers are installed.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running nvidia-smi: {e}")
        sys.exit(1)


def check_model_config(model_name, config_file='model_configs.yaml'):
    """Check if model configuration exists in YAML file."""
    if not os.path.exists(config_file):
        print(f"❌ Model config file not found: {config_file}")
        return False
    
    with open(config_file, 'r') as f:
        configs = yaml.safe_load(f)
    
    if 'models' not in configs:
        print(f"❌ Invalid config file format: {config_file}")
        return False
    
    return model_name in configs['models']


def add_model_config_template(model_name, config_file='model_configs.yaml'):
    """Add a template configuration for the model (for Qwen-7B specifically)."""
    
    # Qwen-7B configuration based on HuggingFace specs
    qwen_7b_config = {
        'num_layers': 32,
        'num_q_heads': 32,
        'num_kv_heads': 32,
        'embedding_dim': 4096,
        'mlp_hidden_dim': 11008,  # Typically 2.75 * embedding_dim for Qwen
        'max_position_embeddings': 8192,
        'use_gated_mlp': True,
        'use_bias': False,
        'use_qkv_bias': True,
        'activation': 'silu',
        'norm': 'rms_norm',
        'post_attn_norm': True,
        'vocab_size': 151936,
        'is_neox_style': True,
        'rope_theta': 10000.0,
        'rope_scaling': None,
        'partial_rotary_factor': 1.0,
        'no_tensor_parallel': False
    }
    
    # For other models, provide a generic template
    generic_config = {
        'num_layers': 32,
        'num_q_heads': 32,
        'num_kv_heads': 32,
        'embedding_dim': 4096,
        'mlp_hidden_dim': 11008,
        'max_position_embeddings': 4096,
        'use_gated_mlp': True,
        'use_bias': False,
        'use_qkv_bias': False,
        'activation': 'silu',
        'norm': 'rms_norm',
        'post_attn_norm': True,
        'vocab_size': 32000,
        'is_neox_style': True,
        'rope_theta': 10000.0,
        'rope_scaling': None,
        'partial_rotary_factor': 1.0,
        'no_tensor_parallel': False
    }
    
    # Choose config based on model name
    if 'Qwen-7B' in model_name or 'Qwen/Qwen-7B' == model_name:
        new_config = qwen_7b_config
    else:
        new_config = generic_config
        print(f"\n⚠️  Using generic model configuration template.")
        print(f"📝 Please verify and update the configuration in {config_file}")
        print(f"   You can find the correct values in the model's HuggingFace config.json")
    
    # Load existing configs
    with open(config_file, 'r') as f:
        configs = yaml.safe_load(f)
    
    # Add new model config
    if 'models' not in configs:
        configs['models'] = {}
    
    configs['models'][model_name] = new_config
    
    # Save updated configs
    with open(config_file, 'w') as f:
        yaml.dump(configs, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Added configuration for {model_name} to {config_file}")
    return True


def run_profiling(model_name, gpu_type, num_gpus, tensor_parallel_sizes, max_tokens=4096):
    """Run MLP and Attention profiling for the model."""
    
    print("\n" + "="*80)
    print("🚀 Starting Profiling Process")
    print("="*80)
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_base_dir = f"profiling_outputs_{timestamp}"
    
    # Step 1: MLP Profiling
    print("\n📊 Step 1/2: MLP Profiling")
    print("-" * 80)
    
    mlp_cmd = [
        'python', '-m', 'vidur.profiling.mlp.main',
        '--models', model_name,
        '--num_gpus', str(num_gpus),
        '--num_tensor_parallel_workers', *[str(s) for s in tensor_parallel_sizes],
        '--max_tokens', str(max_tokens),
        '--output_dir', output_base_dir
    ]
    
    print(f"Running: {' '.join(mlp_cmd)}")
    try:
        subprocess.run(mlp_cmd, check=True)
        print("✅ MLP profiling completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ MLP profiling failed: {e}")
        return False
    
    # Step 2: Attention Profiling
    print("\n📊 Step 2/2: Attention Profiling")
    print("-" * 80)
    
    attention_cmd = [
        'python', '-m', 'vidur.profiling.attention.main',
        '--models', model_name,
        '--num_gpus', str(num_gpus),
        '--num_tensor_parallel_workers', *[str(s) for s in tensor_parallel_sizes],
        '--max_model_len', str(max_tokens),
        '--max_seq_len', str(max_tokens),
        '--output_dir', output_base_dir
    ]
    
    print(f"Running: {' '.join(attention_cmd)}")
    try:
        subprocess.run(attention_cmd, check=True)
        print("✅ Attention profiling completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Attention profiling failed: {e}")
        return False
    
    # Step 3: Copy results to the correct location
    print("\n📂 Step 3/3: Moving profiling results to data directory")
    print("-" * 80)
    
    # Find the latest profiling output directories
    mlp_dirs = sorted(Path(output_base_dir).glob('mlp/*'))
    attention_dirs = sorted(Path(output_base_dir).glob('attention/*'))
    
    if not mlp_dirs or not attention_dirs:
        print("❌ Could not find profiling output directories")
        return False
    
    mlp_output_dir = mlp_dirs[-1]
    attention_output_dir = attention_dirs[-1]
    
    # Target directory
    target_dir = Path('data/profiling/compute') / gpu_type / model_name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy MLP results
    mlp_source = mlp_output_dir / model_name / 'mlp.csv'
    mlp_target = target_dir / 'mlp.csv'
    
    if mlp_source.exists():
        shutil.copy2(mlp_source, mlp_target)
        print(f"✅ Copied MLP profiling data to: {mlp_target}")
    else:
        print(f"⚠️  MLP profiling data not found at: {mlp_source}")
    
    # Copy Attention results
    attention_source = attention_output_dir / model_name / 'attention.csv'
    attention_target = target_dir / 'attention.csv'
    
    if attention_source.exists():
        shutil.copy2(attention_source, attention_target)
        print(f"✅ Copied Attention profiling data to: {attention_target}")
    else:
        print(f"⚠️  Attention profiling data not found at: {attention_source}")
    
    print("\n" + "="*80)
    print("🎉 Profiling Complete!")
    print("="*80)
    print(f"\n📁 Profiling data saved to: {target_dir}")
    print(f"📊 You can now run simulations with model: {model_name} on device: {gpu_type}")
    print(f"\nExample command:")
    print(f"  python run.py prefill {model_name} {gpu_type.upper()} --batch_size 2 --sequence_length 128")
    
    # Cleanup temporary output directory (optional)
    print(f"\n🗑️  Temporary profiling outputs are in: {output_base_dir}")
    print(f"   You can delete this directory after verifying the results.")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Auto Profiling Script for Vidur Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Profile Qwen-7B on current device
  python auto_profile.py --model Qwen/Qwen-7B
  
  # Profile with specific GPU count and tensor parallel sizes
  python auto_profile.py --model Qwen/Qwen-7B --num_gpus 4 --tensor_parallel 1,2,4
  
  # Profile with custom max tokens
  python auto_profile.py --model Qwen/Qwen-7B --max_tokens 8192
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Model name (e.g., Qwen/Qwen-7B, meta-llama/Llama-2-7b-hf)'
    )
    
    parser.add_argument(
        '--num_gpus',
        type=int,
        default=None,
        help='Number of GPUs to use for profiling (default: auto-detect)'
    )
    
    parser.add_argument(
        '--tensor_parallel',
        type=str,
        default='1,2,4,8',
        help='Tensor parallel sizes to profile, comma-separated (default: 1,2,4,8)'
    )
    
    parser.add_argument(
        '--max_tokens',
        type=int,
        default=4096,
        help='Maximum number of tokens to profile (default: 4096)'
    )
    
    parser.add_argument(
        '--skip_config_check',
        action='store_true',
        help='Skip model configuration check and addition'
    )
    
    args = parser.parse_args()
    
    # Parse tensor parallel sizes
    tensor_parallel_sizes = [int(s.strip()) for s in args.tensor_parallel.split(',')]
    
    print("\n" + "="*80)
    print("🔧 Auto Profiling Script for Vidur Simulator")
    print("="*80)
    
    # Step 1: Detect GPU
    print("\n📌 Step 1: Detecting GPU...")
    gpu_type, gpu_count, gpu_name = get_gpu_info()
    print(f"✅ Detected GPU: {gpu_name}")
    print(f"   Type: {gpu_type.upper()}")
    print(f"   Count: {gpu_count}")
    
    # Determine number of GPUs to use
    num_gpus = args.num_gpus if args.num_gpus else gpu_count
    if num_gpus > gpu_count:
        print(f"⚠️  Requested {num_gpus} GPUs but only {gpu_count} available. Using {gpu_count}.")
        num_gpus = gpu_count
    
    print(f"   Using: {num_gpus} GPU(s) for profiling")
    
    # Step 2: Check model configuration
    if not args.skip_config_check:
        print(f"\n📌 Step 2: Checking model configuration for '{args.model}'...")
        
        if check_model_config(args.model):
            print(f"✅ Model configuration found in model_configs.yaml")
        else:
            print(f"⚠️  Model configuration not found in model_configs.yaml")
            response = input(f"   Would you like to add a template configuration? (y/n): ")
            
            if response.lower() == 'y':
                add_model_config_template(args.model)
            else:
                print(f"\n❌ Please add model configuration to model_configs.yaml manually")
                print(f"   Refer to existing models for the correct format")
                sys.exit(1)
    
    # Step 3: Run profiling
    print(f"\n📌 Step 3: Running profiling for '{args.model}' on {gpu_type.upper()}...")
    
    success = run_profiling(
        args.model,
        gpu_type,
        num_gpus,
        tensor_parallel_sizes,
        args.max_tokens
    )
    
    if success:
        print("\n✨ All done! Your model is now ready for simulation.")
        sys.exit(0)
    else:
        print("\n❌ Profiling failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == '__main__':
    main()

