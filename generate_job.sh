#!/bin/bash
#SBATCH --job-name=cipherlens-generate
#SBATCH --output=%j_generate_out.log
#SBATCH --error=%j_generate_error.log
#SBATCH --time=2:0:0
#SBATCH --partition=short
#SBATCH --qos=short
#SBATCH --mem=32G
#SBATCH --ntasks-per-node=8
#SBATCH --account=ravi

source ~/miniconda3/bin/activate cipherlens
cd ~/cipherlens

# Generate V4 dataset (no GPU needed — pure Python/NumPy)
# ~25k samples x 22 ciphers = 550k rows, estimated ~40-60 min
python backend/scripts/generate_dataset_v4.py \
    --samples 25000 \
    --out data/cipher_MASTER_FULL_V4.csv \
    --seed 42

# Compress to save disk space
echo "Compressing..."
gzip -k data/cipher_MASTER_FULL_V4.csv

echo "Dataset generation complete!"
ls -lh data/
