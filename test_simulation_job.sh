#!/bin/bash
#SBATCH --job-name=test_simulation
#SBATCH --partition=msigpu
#SBATCH --gres=gpu:h100:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=logs/test_sim_%j.out
#SBATCH --error=logs/test_sim_%j.err

# Create logs directory
mkdir -p logs

# Load modules
module load cuda/12.1.1

# Print info
echo "=========================================="
echo "Testing Simulation with Existing Data"
echo "Job started at: $(date)"
echo "Running on node: $(hostname)"
echo "=========================================="
echo ""
nvidia-smi
echo ""

# Change to project directory
cd /users/7/li003385/workspace/Sai_speculative_vidur

# Install dependencies
echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt --quiet

# Test 1: Prefill simulation with Llama-2-7b
echo ""
echo "=========================================="
echo "Test 1: Prefill Simulation (Llama-2-7b)"
echo "=========================================="
python3 run.py prefill meta-llama/Llama-2-7b-hf A100 --batch_size 2 --sequence_length 128

# Test 2: Decode simulation with Llama-2-7b
echo ""
echo "=========================================="
echo "Test 2: Decode Simulation (Llama-2-7b)"
echo "=========================================="
python3 run.py decode meta-llama/Llama-2-7b-hf A100 --batch_size 2 --tokens_to_generate 4 --kv_cache_length 128

# Test 3: Test with Qwen-72B (existing profiling data)
echo ""
echo "=========================================="
echo "Test 3: Prefill Simulation (Qwen-72B)"
echo "=========================================="
python3 run.py prefill Qwen/Qwen-72B A100 --batch_size 2 --sequence_length 128

echo ""
echo "=========================================="
echo "All tests completed at: $(date)"
echo "=========================================="

