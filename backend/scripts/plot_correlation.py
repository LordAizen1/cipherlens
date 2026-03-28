import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def main():
    print("Loading V3 dataset...")
    df = pd.read_csv("/Users/maulikmahey/Documents/IIIT-D/SEMESTER-8/BTP/cipher_MASTER_FULL_V3.csv")
    
    features = [
        "length", "entropy", "compression", "bigram_entropy", "trigram_entropy",
        "uniformity", "unique_ratio", "transition_var", "run_length_mean",
        "run_length_var", "ioc", "ioc_variance", "digit_ratio", "alpha_ratio"
    ]
    
    print("Computing correlation matrix...")
    corr_matrix = df[features].corr()
    
    print("Plotting heatmap...")
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Feature Correlation Matrix - CipherLens V3 Dataset")
    plt.tight_layout()
    
    # Save to frontend public folder so it can be viewed directly
    out_dir = "../frontend/public/plots"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "feature_correlation.png")
    
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved correlation heatmap to {out_path}")
    
    # Plot 2: Average IoC by Cipher Family
    print("Plotting average IoC and Entropy by cipher...")
    
    plt.figure(figsize=(14, 7))
    sns.scatterplot(data=df.sample(20000, random_state=42), x='ioc', y='entropy', hue='cipher', alpha=0.5, palette='tab20')
    plt.title("IoC vs Entropy across Ciphers (20k sample)")
    plt.tight_layout()
    
    out_path_scatter = os.path.join(out_dir, "ioc_vs_entropy.png")
    plt.savefig(out_path_scatter, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved scatterplot to {out_path_scatter}")

if __name__ == "__main__":
    main()
