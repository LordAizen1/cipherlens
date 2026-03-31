#!/bin/bash
#SBATCH --job-name=cipherlens-hybrid
#SBATCH --output=%j_out.log
#SBATCH --error=%j_error.log
#SBATCH --time=1:0:0
#SBATCH --partition=short
#SBATCH --qos=short
#SBATCH --mem=32G
#SBATCH --ntasks-per-node=8
#SBATCH --gres=gpu:3g.40gb:1
#SBATCH --account=ravi

source ~/miniconda3/bin/activate cipherlens
cd ~/cipherlens/backend
python scripts/train_hybrid.py
