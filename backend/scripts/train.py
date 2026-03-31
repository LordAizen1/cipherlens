import os
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, '..', '..', 'data', 'cipher_MASTER_FULL_V3_shuffled.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'app', 'models')

def train_models():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    print(f"Loading data from {DATA_PATH}...")
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"Error: Could not find dataset at {DATA_PATH}")
        return

    features = [
        "length", "entropy", "compression", "bigram_entropy", "trigram_entropy",
        "uniformity", "unique_ratio", "transition_var", "run_length_mean",
        "run_length_var", "ioc", "ioc_variance", "digit_ratio", "alpha_ratio"
    ]
    
    X = df[features]
    y_family = df['family']
    
    # Encode Family targets for XGBoost
    family_le = LabelEncoder()
    y_fam_enc = family_le.fit_transform(y_family)
    
    family_le_path = os.path.join(MODEL_DIR, "family_label_encoder.pkl")
    joblib.dump(family_le, family_le_path)

    print("Training XGBoost Family Classifier (Stage 1)...")
    family_clf = XGBClassifier(
        n_estimators=700,
        max_depth=10,
        learning_rate=0.03,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="mlogloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1
    )
    family_clf.fit(X, y_fam_enc)
    
    family_model_path = os.path.join(MODEL_DIR, "family_classifier.pkl")
    joblib.dump(family_clf, family_model_path)
    print(f"Saved: {family_model_path}")

    # Train Cipher Classifiers for each family (Stage 2)
    families = df['family'].unique()
    for family in families:
        print(f"Training Cipher Classifier for family: {family}...")
        
        family_df = df[df['family'] == family]
        X_fam = family_df[features]
        y_fam = family_df['cipher']
        
        # Encode Cipher targets for XGBoost
        cipher_le = LabelEncoder()
        y_fam_enc_cipher = cipher_le.fit_transform(y_fam)
        
        cipher_le_path = os.path.join(MODEL_DIR, f"cipher_le_{family}.pkl")
        joblib.dump(cipher_le, cipher_le_path)
        
        num_classes = len(cipher_le.classes_)
        if num_classes == 1:
            print(f"Skipping model training for {family} as it only has 1 class.")
            continue
            
        cipher_clf = XGBClassifier(
            n_estimators=600,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="mlogloss",
            tree_method="hist",
            random_state=42,
            n_jobs=-1
        )
        cipher_clf.fit(X_fam, y_fam_enc_cipher)
        
        cipher_model_path = os.path.join(MODEL_DIR, f"cipher_classifier_{family}.pkl")
        joblib.dump(cipher_clf, cipher_model_path)
        print(f"Saved: {cipher_model_path}")

    print("Training complete! XGBoost Models saved gracefully.")

if __name__ == "__main__":
    train_models()
