import pandas as pd
import os

base = os.path.dirname(os.path.abspath(__file__))
src  = os.path.join(base, 'data', 'cipher_MASTER_FULL_V3_shuffled.csv')
dst  = os.path.join(base, 'data', 'cipher_MASTER_FULL_V3_shuffled.csv.gz')

print(f'Reading {src}...')
df = pd.read_csv(src)
print(f'Shape: {df.shape}')
df.to_csv(dst, index=False, compression='gzip')
size = os.path.getsize(dst) / 1024 / 1024
print(f'Done. Compressed size: {size:.1f} MB')
