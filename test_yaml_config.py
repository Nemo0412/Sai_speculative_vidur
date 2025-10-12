#!/usr/bin/env python3
"""
Test script to demonstrate YAML model configuration loading.
This script shows how model configurations are loaded from model_configs.yaml.
"""

from vidur.config.model_config import BaseModelConfig
from vidur.logger import init_logger

logger = init_logger(__name__)

def test_model_loading():
    """Test loading various models from YAML configuration"""
    
    models_to_test = [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-70b-hf",
        "meta-llama/Meta-Llama-3-8B",
        "Qwen/Qwen-72B",
    ]
    
    print("="*70)
    print("Testing YAML Model Configuration Loading")
    print("="*70)
    
    for model_name in models_to_test:
        print(f"\n📦 Loading model: {model_name}")
        try:
            config = BaseModelConfig.create_from_name(model_name)
            print(f"   ✅ Successfully loaded!")
            print(f"   └─ Layers: {config.num_layers}")
            print(f"   └─ Q Heads: {config.num_q_heads}")
            print(f"   └─ KV Heads: {config.num_kv_heads}")
            print(f"   └─ Embedding Dim: {config.embedding_dim}")
            print(f"   └─ MLP Hidden Dim: {config.mlp_hidden_dim}")
            print(f"   └─ Max Position Embeddings: {config.max_position_embeddings}")
            print(f"   └─ Vocab Size: {config.vocab_size}")
            print(f"   └─ Activation: {config.activation}")
            print(f"   └─ Norm: {config.norm}")
        except Exception as e:
            print(f"   ❌ Failed to load: {e}")
    
    print("\n" + "="*70)
    print("✅ All models loaded successfully!")
    print("="*70)

if __name__ == "__main__":
    test_model_loading()

