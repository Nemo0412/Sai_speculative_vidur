#!/usr/bin/env python3
"""
Test script to verify auto profiling configuration without GPU
This script tests the configuration loading and validation logic
"""

import yaml
import sys
from pathlib import Path


def test_model_config_exists(model_name, config_file='model_configs.yaml'):
    """Test if model configuration exists"""
    print(f"\n📋 Testing model configuration for: {model_name}")
    print("-" * 60)
    
    if not Path(config_file).exists():
        print(f"❌ Config file not found: {config_file}")
        return False
    
    with open(config_file, 'r') as f:
        configs = yaml.safe_load(f)
    
    if 'models' not in configs:
        print(f"❌ Invalid config file format")
        return False
    
    if model_name not in configs['models']:
        print(f"❌ Model '{model_name}' not found in config")
        print(f"   Available models:")
        for m in configs['models'].keys():
            print(f"     - {m}")
        return False
    
    print(f"✅ Model configuration found")
    
    # Display configuration
    config = configs['models'][model_name]
    print(f"\n📊 Configuration details:")
    for key, value in config.items():
        print(f"   {key:30s}: {value}")
    
    # Validate required fields
    required_fields = [
        'num_layers', 'num_q_heads', 'num_kv_heads', 'embedding_dim',
        'mlp_hidden_dim', 'max_position_embeddings', 'use_gated_mlp',
        'use_bias', 'use_qkv_bias', 'activation', 'norm', 'post_attn_norm',
        'vocab_size', 'is_neox_style', 'rope_theta', 'partial_rotary_factor',
        'no_tensor_parallel'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in config:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n⚠️  Missing required fields:")
        for field in missing_fields:
            print(f"   - {field}")
        return False
    
    print(f"\n✅ All required fields present")
    
    # Validate field values
    print(f"\n🔍 Validating field values...")
    
    # Check activation
    if config['activation'] not in ['silu', 'gelu']:
        print(f"❌ Invalid activation: {config['activation']} (must be 'silu' or 'gelu')")
        return False
    print(f"   ✓ activation: {config['activation']}")
    
    # Check norm
    if config['norm'] not in ['rms_norm', 'layer_norm']:
        print(f"❌ Invalid norm: {config['norm']} (must be 'rms_norm' or 'layer_norm')")
        return False
    print(f"   ✓ norm: {config['norm']}")
    
    # Check gated_mlp consistency
    if config['use_gated_mlp'] and config['activation'] != 'silu':
        print(f"❌ use_gated_mlp=True requires activation='silu'")
        return False
    print(f"   ✓ use_gated_mlp: {config['use_gated_mlp']}")
    
    # Check numeric fields
    numeric_fields = ['num_layers', 'num_q_heads', 'num_kv_heads', 'embedding_dim', 
                     'mlp_hidden_dim', 'max_position_embeddings', 'vocab_size']
    for field in numeric_fields:
        if not isinstance(config[field], int) or config[field] <= 0:
            print(f"❌ {field} must be a positive integer, got: {config[field]}")
            return False
    print(f"   ✓ All numeric fields valid")
    
    # Check head compatibility
    if config['embedding_dim'] % config['num_q_heads'] != 0:
        print(f"❌ embedding_dim ({config['embedding_dim']}) must be divisible by num_q_heads ({config['num_q_heads']})")
        return False
    print(f"   ✓ Head size: {config['embedding_dim'] // config['num_q_heads']}")
    
    print(f"\n✅ Configuration is valid!")
    return True


def test_auto_profile_script():
    """Test if auto_profile.py exists and has correct permissions"""
    print(f"\n📋 Testing auto_profile.py script")
    print("-" * 60)
    
    script_path = Path('auto_profile.py')
    
    if not script_path.exists():
        print(f"❌ auto_profile.py not found")
        return False
    
    print(f"✅ auto_profile.py exists")
    
    # Check if executable
    import os
    if os.access(script_path, os.X_OK):
        print(f"✅ auto_profile.py is executable")
    else:
        print(f"⚠️  auto_profile.py is not executable (optional)")
        print(f"   You can make it executable with: chmod +x auto_profile.py")
    
    return True


def test_quick_profile_script():
    """Test if quick_profile.sh exists and has correct permissions"""
    print(f"\n📋 Testing quick_profile.sh script")
    print("-" * 60)
    
    script_path = Path('quick_profile.sh')
    
    if not script_path.exists():
        print(f"❌ quick_profile.sh not found")
        return False
    
    print(f"✅ quick_profile.sh exists")
    
    # Check if executable
    import os
    if os.access(script_path, os.X_OK):
        print(f"✅ quick_profile.sh is executable")
    else:
        print(f"⚠️  quick_profile.sh is not executable")
        print(f"   Make it executable with: chmod +x quick_profile.sh")
    
    return True


def test_directory_structure():
    """Test if profiling directory structure exists"""
    print(f"\n📋 Testing directory structure")
    print("-" * 60)
    
    base_dir = Path('data/profiling/compute')
    
    if not base_dir.exists():
        print(f"⚠️  Base profiling directory does not exist: {base_dir}")
        print(f"   This is OK - it will be created during profiling")
        return True
    
    print(f"✅ Base profiling directory exists: {base_dir}")
    
    # Check for existing GPU types
    gpu_types = ['a100', 'h100', 'a40']
    for gpu_type in gpu_types:
        gpu_dir = base_dir / gpu_type
        if gpu_dir.exists():
            print(f"   ✓ {gpu_type} directory exists")
            # List models
            models = [d.relative_to(gpu_dir) for d in gpu_dir.rglob('*.csv')]
            if models:
                print(f"     Profiled models: {len(set(str(m.parent) for m in models))}")
        else:
            print(f"   - {gpu_type} directory not found (will be created)")
    
    return True


def main():
    print("=" * 60)
    print("🧪 Auto Profiling Configuration Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Check scripts
    if not test_auto_profile_script():
        all_passed = False
    
    if not test_quick_profile_script():
        all_passed = False
    
    # Test 2: Check directory structure
    if not test_directory_structure():
        all_passed = False
    
    # Test 3: Check model configurations
    test_models = [
        'Qwen/Qwen-7B',
        'meta-llama/Llama-2-7b-hf',
        'Qwen/Qwen-72B',
    ]
    
    for model in test_models:
        if not test_model_config_exists(model):
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
        print("\n🎉 Your auto profiling setup is ready to use!")
        print("\nNext steps:")
        print("  1. Ensure you're on a machine with GPU")
        print("  2. Activate virtual environment: source .venv/bin/activate")
        print("  3. Start Ray: ray start --head")
        print("  4. Run profiling: ./quick_profile.sh Qwen/Qwen-7B")
    else:
        print("❌ Some tests failed")
        print("\n⚠️  Please fix the issues above before running profiling")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()

