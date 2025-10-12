#!/usr/bin/env python3
"""
Test script for leshu_test_model to verify:
1. Custom model loading from YAML
2. Prefill simulation functionality
3. Decode simulation functionality
"""

from vidur.config.model_config import BaseModelConfig
from vidur.logger import init_logger
import subprocess
import sys

logger = init_logger(__name__)

def test_model_loading():
    """Test if leshu_test_model can be loaded from YAML"""
    print("="*70)
    print("TEST 1: Loading leshu_test_model from YAML")
    print("="*70)
    
    try:
        config = BaseModelConfig.create_from_name("leshu/leshu_test_model")
        print("✅ Model loaded successfully!")
        print(f"\n📋 Model Configuration:")
        print(f"   Name: leshu/leshu_test_model")
        print(f"   Layers: {config.num_layers}")
        print(f"   Q Heads: {config.num_q_heads}")
        print(f"   KV Heads: {config.num_kv_heads}")
        print(f"   Embedding Dim: {config.embedding_dim}")
        print(f"   MLP Hidden Dim: {config.mlp_hidden_dim}")
        print(f"   Max Position Embeddings: {config.max_position_embeddings}")
        print(f"   Vocab Size: {config.vocab_size}")
        print(f"   Activation: {config.activation}")
        print(f"   Norm: {config.norm}")
        print(f"   Use Gated MLP: {config.use_gated_mlp}")
        print(f"   RoPE Theta: {config.rope_theta}")
        return True
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False

def test_prefill_simulation():
    """Test prefill simulation with leshu_test_model"""
    print("\n" + "="*70)
    print("TEST 2: Running Prefill Simulation")
    print("="*70)
    
    cmd = [
        "python", "run.py",
        "prefill",
        "leshu/leshu_test_model",
        "A100",
        "--batch_size", "2",
        "--sequence_length", "128"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print("✅ Prefill simulation completed successfully!")
        
        # Check if latency results are in output
        if "PREFILL LATENCY" in result.stdout:
            print("✅ Latency results generated successfully!")
            # Extract and display key metrics
            for line in result.stdout.split('\n'):
                if 'Mean:' in line or 'Median:' in line or 'P95:' in line or 'P99:' in line:
                    print(f"   {line.strip()}")
        else:
            print("⚠️  No latency results found in output")
            
        return True
    except subprocess.TimeoutExpired:
        print("❌ Simulation timed out after 120 seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Simulation failed with return code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_decode_simulation():
    """Test decode simulation with leshu_test_model"""
    print("\n" + "="*70)
    print("TEST 3: Running Decode Simulation")
    print("="*70)
    
    cmd = [
        "python", "run.py",
        "decode",
        "leshu/leshu_test_model",
        "A100",
        "--batch_size", "2",
        "--tokens_to_generate", "4",
        "--kv_cache_length", "128"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print("✅ Decode simulation completed successfully!")
        
        # Check if latency results are in output
        if "DECODE LATENCY" in result.stdout:
            print("✅ Latency results generated successfully!")
            # Extract and display key metrics
            for line in result.stdout.split('\n'):
                if ('DECODE LATENCY' in line or 'Mean:' in line or 
                    'Median:' in line or 'P95:' in line or 'P99:' in line):
                    print(f"   {line.strip()}")
        else:
            print("⚠️  No decode latency results found in output")
            
        return True
    except subprocess.TimeoutExpired:
        print("❌ Simulation timed out after 120 seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Simulation failed with return code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🧪 Testing leshu_test_model Custom Model Functionality")
    print("="*70)
    
    results = []
    
    # Test 1: Model Loading
    results.append(("Model Loading", test_model_loading()))
    
    # Test 2: Prefill Simulation
    if results[0][1]:  # Only run if model loaded successfully
        results.append(("Prefill Simulation", test_prefill_simulation()))
    else:
        print("\n⚠️  Skipping prefill simulation (model loading failed)")
        results.append(("Prefill Simulation", False))
    
    # Test 3: Decode Simulation
    if results[0][1]:  # Only run if model loaded successfully
        results.append(("Decode Simulation", test_decode_simulation()))
    else:
        print("\n⚠️  Skipping decode simulation (model loading failed)")
        results.append(("Decode Simulation", False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name:.<50} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("="*70)
    if all_passed:
        print("🎉 All tests passed! Custom model functionality is working!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print("="*70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

