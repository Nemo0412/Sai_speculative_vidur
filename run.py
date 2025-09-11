#!/usr/bin/env python3
"""
Custom script to run Vidur simulator with simplified command line interface.
Usage:
    python run.py prefill llama-70b H100 --batch_size 4 --sequence_length 256
    python run.py decode llama-70b H100 --batch_size 8 --tokens_to_generate 4 --kv_cache_length 1024
"""

import argparse
import subprocess
import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime


def get_model_name(model_input):
    """Convert user input to proper model name for Vidur"""
    model_mapping = {
        "llama-70b": "meta-llama/Llama-2-70b-hf",
        "llama-7b": "meta-llama/Llama-2-7b-hf", 
        "llama3-8b": "meta-llama/Meta-Llama-3-8B",
        "llama3-70b": "meta-llama/Meta-Llama-3-70B",
        "codellama-34b": "codellama/CodeLlama-34b-Instruct-hf",
        "internlm-20b": "internlm/internlm-20b",
        "qwen-72b": "Qwen/Qwen-72B"
    }
    return model_mapping.get(model_input.lower(), model_input)


def get_device_name(device_input):
    """Convert user input to proper device name for Vidur"""
    device_mapping = {
        "h100": "h100",
        "a100": "a100", 
        "a40": "a40"
    }
    return device_mapping.get(device_input.lower(), device_input)


def parse_latency_results(output_dir):
    """Parse and display latency results from simulation output"""
    try:
        # Find the most recent output directory
        output_path = Path(output_dir)
        if not output_path.exists():
            print(f"❌ Output directory {output_dir} not found")
            return None
            
        # Get all timestamped directories and find the latest one
        timestamp_dirs = [d for d in output_path.iterdir() if d.is_dir() and d.name.startswith('2025-')]
        if not timestamp_dirs:
            print(f"❌ No simulation results found in {output_dir}")
            return None
            
        latest_dir = max(timestamp_dirs, key=lambda x: x.name)
        print(f"📁 Reading results from: {latest_dir}")
        
        # Read request metrics
        metrics_file = latest_dir / "request_metrics.csv"
        if not metrics_file.exists():
            print(f"❌ Metrics file not found: {metrics_file}")
            return None
            
        df = pd.read_csv(metrics_file)
        
        # Calculate latency statistics
        results = {}
        
        if 'prefill_e2e_time' in df.columns:
            prefill_times = df['prefill_e2e_time'].dropna()
            if len(prefill_times) > 0:
                results['prefill'] = {
                    'mean': prefill_times.mean(),
                    'median': prefill_times.median(),
                    'min': prefill_times.min(),
                    'max': prefill_times.max(),
                    'std': prefill_times.std(),
                    'p95': prefill_times.quantile(0.95),
                    'p99': prefill_times.quantile(0.99)
                }
        
        if 'decode_time_execution_plus_preemption_normalized' in df.columns:
            decode_times = df['decode_time_execution_plus_preemption_normalized'].dropna()
            if len(decode_times) > 0:
                results['decode'] = {
                    'mean': decode_times.mean(),
                    'median': decode_times.median(),
                    'min': decode_times.min(),
                    'max': decode_times.max(),
                    'std': decode_times.std(),
                    'p95': decode_times.quantile(0.95),
                    'p99': decode_times.quantile(0.99)
                }
        
        # Display results
        print("\n" + "="*60)
        print("📊 SIMULATION RESULTS - LATENCY METRICS")
        print("="*60)
        
        if 'prefill' in results:
            print(f"\n🔵 PREFILL LATENCY (seconds):")
            print(f"   Mean:    {results['prefill']['mean']:.6f}s")
            print(f"   Median:  {results['prefill']['median']:.6f}s")
            print(f"   Min:     {results['prefill']['min']:.6f}s")
            print(f"   Max:     {results['prefill']['max']:.6f}s")
            print(f"   P95:     {results['prefill']['p95']:.6f}s")
            print(f"   P99:     {results['prefill']['p99']:.6f}s")
            print(f"   Std:     {results['prefill']['std']:.6f}s")
        
        if 'decode' in results:
            print(f"\n🟢 DECODE LATENCY (seconds):")
            print(f"   Mean:    {results['decode']['mean']:.6f}s")
            print(f"   Median:  {results['decode']['median']:.6f}s")
            print(f"   Min:     {results['decode']['min']:.6f}s")
            print(f"   Max:     {results['decode']['max']:.6f}s")
            print(f"   P95:     {results['decode']['p95']:.6f}s")
            print(f"   P99:     {results['decode']['p99']:.6f}s")
            print(f"   Std:     {results['decode']['std']:.6f}s")
        
        # Additional info
        print(f"\n📈 SIMULATION INFO:")
        print(f"   Total requests: {len(df)}")
        print(f"   Prefill tokens: {df['request_num_prefill_tokens'].iloc[0] if 'request_num_prefill_tokens' in df.columns else 'N/A'}")
        print(f"   Decode tokens:  {df['request_num_decode_tokens'].iloc[0] if 'request_num_decode_tokens' in df.columns else 'N/A'}")
        
        print("="*60)
        
        return results
        
    except Exception as e:
        print(f"❌ Error parsing results: {e}")
        return None


def run_prefill_simulation(model, device, batch_size, sequence_length, output_dir="simulator_output"):
    """Run prefill simulation"""
    model_name = get_model_name(model)
    device_name = get_device_name(device)
    
    # Calculate prefill tokens (sequence_length) and decode tokens (small number for prefill)
    prefill_tokens = sequence_length
    decode_tokens = 1  # Minimal decode for prefill measurement
    
    cmd = [
        "python", "-m", "vidur.main",
        "--replica_config_device", device_name,
        "--replica_config_model_name", model_name,
        "--cluster_config_num_replicas", "1",
        "--replica_config_tensor_parallel_size", "1",
        "--replica_config_num_pipeline_stages", "1",
        "--request_generator_config_type", "synthetic",
        "--synthetic_request_generator_config_num_requests", str(batch_size),
        "--length_generator_config_type", "fixed",
        "--fixed_request_length_generator_config_prefill_tokens", str(prefill_tokens),
        "--fixed_request_length_generator_config_decode_tokens", str(decode_tokens),
        "--interval_generator_config_type", "poisson",
        "--poisson_request_interval_generator_config_qps", "10.0",  # High QPS to batch requests quickly
        "--replica_scheduler_config_type", "sarathi",
        "--sarathi_scheduler_config_batch_size_cap", str(batch_size),
        "--sarathi_scheduler_config_chunk_size", "512",
        "--execution_time_predictor_config_type", "random_forrest",
        "--metrics_config_output_dir", output_dir,
        "--no-metrics_config_store_plots",  # Disable plots to avoid Chrome dependency
        "--no-metrics_config_enable_chrome_trace",
        "--time_limit", "60"  # 1 minute timeout
    ]
    
    print(f"Running prefill simulation:")
    print(f"  Model: {model_name}")
    print(f"  Device: {device_name}")
    print(f"  Batch size: {batch_size}")
    print(f"  Sequence length: {sequence_length}")
    print(f"  Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Simulation completed successfully!")
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Parse and display latency results
        parse_latency_results(output_dir)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Simulation failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_decode_simulation(model, device, batch_size, tokens_to_generate, kv_cache_length, output_dir="simulator_output"):
    """Run decode simulation"""
    model_name = get_model_name(model)
    device_name = get_device_name(device)
    
    # For decode, we need prefill tokens (kv_cache_length) and decode tokens (tokens_to_generate)
    prefill_tokens = kv_cache_length
    decode_tokens = tokens_to_generate
    
    cmd = [
        "python", "-m", "vidur.main",
        "--replica_config_device", device_name,
        "--replica_config_model_name", model_name,
        "--cluster_config_num_replicas", "1",
        "--replica_config_tensor_parallel_size", "1",
        "--replica_config_num_pipeline_stages", "1",
        "--request_generator_config_type", "synthetic",
        "--synthetic_request_generator_config_num_requests", str(batch_size),
        "--length_generator_config_type", "fixed",
        "--fixed_request_length_generator_config_prefill_tokens", str(prefill_tokens),
        "--fixed_request_length_generator_config_decode_tokens", str(decode_tokens),
        "--interval_generator_config_type", "poisson",
        "--poisson_request_interval_generator_config_qps", "10.0",  # High QPS to batch requests quickly
        "--replica_scheduler_config_type", "sarathi",
        "--sarathi_scheduler_config_batch_size_cap", str(batch_size),
        "--sarathi_scheduler_config_chunk_size", "512",
        "--execution_time_predictor_config_type", "random_forrest",
        "--metrics_config_output_dir", output_dir,
        "--no-metrics_config_store_plots",  # Disable plots to avoid Chrome dependency
        "--no-metrics_config_enable_chrome_trace",
        "--time_limit", "60"  # 1 minute timeout
    ]
    
    print(f"Running decode simulation:")
    print(f"  Model: {model_name}")
    print(f"  Device: {device_name}")
    print(f"  Batch size: {batch_size}")
    print(f"  Tokens to generate: {tokens_to_generate}")
    print(f"  KV cache length: {kv_cache_length}")
    print(f"  Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Simulation completed successfully!")
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Parse and display latency results
        parse_latency_results(output_dir)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Simulation failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run Vidur simulator with simplified interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py prefill llama-70b H100 --batch_size 4 --sequence_length 256
  python run.py decode llama-70b H100 --batch_size 8 --tokens_to_generate 4 --kv_cache_length 1024
  python run.py prefill llama-7b A100 --batch_size 8 --sequence_length 512
        """
    )
    
    parser.add_argument("operation", choices=["prefill", "decode"], 
                       help="Operation type: prefill or decode")
    parser.add_argument("model", 
                       help="Model name (e.g., llama-70b, llama-7b, llama3-8b)")
    parser.add_argument("device", 
                       help="GPU device (e.g., H100, A100, A40)")
    
    # Common arguments
    parser.add_argument("--batch_size", type=int, required=True,
                       help="Batch size (number of requests)")
    
    # Prefill-specific arguments
    parser.add_argument("--sequence_length", type=int,
                       help="Input prompt length (for prefill)")
    
    # Decode-specific arguments  
    parser.add_argument("--tokens_to_generate", type=int,
                       help="Number of tokens to generate (for decode)")
    parser.add_argument("--kv_cache_length", type=int,
                       help="KV cache length/context length (for decode)")
    
    # Optional arguments
    parser.add_argument("--output_dir", default="simulator_output",
                       help="Output directory for results")
    
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    
    # Validate arguments based on operation type
    if args.operation == "prefill":
        if args.sequence_length is None:
            print("Error: --sequence_length is required for prefill operation")
            sys.exit(1)
    elif args.operation == "decode":
        if args.tokens_to_generate is None or args.kv_cache_length is None:
            print("Error: --tokens_to_generate and --kv_cache_length are required for decode operation")
            sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run simulation based on operation type
    if args.operation == "prefill":
        success = run_prefill_simulation(
            model=args.model,
            device=args.device,
            batch_size=args.batch_size,
            sequence_length=args.sequence_length,
            output_dir=args.output_dir
        )
    else:  # decode
        success = run_decode_simulation(
            model=args.model,
            device=args.device,
            batch_size=args.batch_size,
            tokens_to_generate=args.tokens_to_generate,
            kv_cache_length=args.kv_cache_length,
            output_dir=args.output_dir
        )
    
    if success:
        print(f"\n✅ Simulation completed successfully!")
        print(f"📁 Results saved to: {args.output_dir}")
        print(f"📊 Check the metrics files in the output directory for latency results")
    else:
        print(f"\n❌ Simulation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
