import pandas as pd
import os

base = os.path.dirname(os.path.abspath(__file__))
src  = os.path.join(base, 'data', 'cipher_MASTER_FULL_V3.csv.gz')
dst  = os.path.join(base, 'data', 'cipher_MASTER_FULL_V3_shuffled.csv')

df = pd.read_csv(src)
print('Shape:', df.shape)
print('Ciphers:\n', df['cipher'].value_counts())
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv(dst, index=False)
print(f'Done. Saved to {dst}')
