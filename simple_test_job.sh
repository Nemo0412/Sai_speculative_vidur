#!/bin/bash
#SBATCH --job-name=simple_test
#SBATCH --partition=msigpu
#SBATCH --gres=gpu:h100:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:10:00
#SBATCH --output=logs/simple_test_%j.out
#SBATCH --error=logs/simple_test_%j.err

# Load modules
module load cuda/12.1.1

# Print info
echo "=========================================="
echo "Simple Test - Prefill Simulation"
echo "Job started at: $(date)"
echo "=========================================="
nvidia-smi
echo ""

# Run ONE simple test
cd /users/7/li003385/workspace/Sai_speculative_vidur
echo "Running prefill simulation..."
python3 run.py prefill meta-llama/Llama-2-7b-hf A100 --batch_size 2 --sequence_length 128

echo ""
echo "Job completed at: $(date)"

