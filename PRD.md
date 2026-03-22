# Product Requirements Document (PRD): Hierarchical Cipher Classification Backend

## 1. Introduction & Objective
The goal of this project is to build a production-ready backend system that receives an unidentified ciphertext and accurately predicts the exact cryptographic algorithm used to generate it. The system will leverage a **Two-Stage Hierarchical Machine Learning Model** based on previous research:
*   **Stage 1:** Classify the cipher into its broad cryptographic family.
*   **Stage 2:** Classify the exact cipher algorithm based on the predicted family.

This PRD provides the necessary blueprints so that AI agents can directly implement the backend data pipelines, model architecture, and serving API.

## 2. Background & Scope
The system is based on classical and modern cipher studies. It leverages 12 distinct statistical text features to identify patterns inherent to different encryption schemas. 

### 2.1 Supported Cipher Families (Stage 1)
1. **Monoalphabetic**
2. **Poly-alphabetic**
3. **Transposition**
4. **Polygraphic + Fractionating**
5. **Modern Block Ciphers**

### 2.2 Supported Ciphers (Stage 2)
*   **Monoalphabetic:** Caesar, Affine, Atbash
*   **Poly-alphabetic:** Vigenère, Autokey, Beaufort, Porta
*   **Transposition:** Columnar
*   **Polygraphic/Fractionating:** Playfair, Foursquare, Hill, Polybius, Nihilist, Bifid, Trifid, ADFGX, ADFGVX
*   **Modern:** TEA, XTEA, Lucifer, LOKI, Misty1

## 3. System Architecture & Flow
The backend will expose a RESTful API end-to-end classification pipeline.

### Step 1: Input Ingestion
*   Receive a raw string of ciphertext via an HTTP POST request.
*   Basic cleaning: handle non-printable characters or whitespace (if applicable).

### Step 2: Feature Extraction Module
The pipeline must extract the following features from the ciphertext in real-time:
1. **Length:** Total number of characters/bytes.
2. **Entropy:** Shannon entropy of character frequencies.
3. **Compression Ratio:** Size after zlib compression / original size.
4. **Bigram Entropy:** Entropy of 2-character sequences.
5. **Trigram Entropy:** Entropy of 3-character sequences.
6. **Uniformity:** Standard deviation of frequency counts.
7. **Unique Symbol Ratio:** Number of unique characters / total length.
8. **Transition Variance:** Variance of character transitions ($C_i$ to $C_{i+1}$).
9. **Run-Length Mean:** Average length of consecutive identical characters.
10. **Run-Length Variance:** Variance of run-lengths.
11. **Index of Coincidence (IoC):** Probability that two randomly drawn characters match.
12. **IoC Variance (Periodicity):** Variance of IoC across different slice periods (simulating key lengths 2 to 9).

### Step 3: Inference Engine
*   **Model Server:** Load pre-trained models (e.g., Random Forest, XGBoost, or Neural Networks).
*   **Stage 1 Inference:** Pass the 12 features to the Family Classifier Model. Get the predicted family and confidence score.
*   **Stage 2 Inference:** Dynamically route the features to the corresponding Cipher Classifier Model specific to the predicted family. Get the exact cipher prediction and confidence score.

### Step 4: Output Formatting
Return a structured JSON response to the user.

## 4. API Specifications
### `POST /api/v1/classify-cipher`
#### Request Payload
```json
{
  "ciphertext": "VJKUKUCVGUVOGUUCIG"
}
```

#### Response Payload (200 OK)
```json
{
  "status": "success",
  "predictions": {
    "family": {
      "predicted_class": "monoalphabetic",
      "confidence": 0.98
    },
    "cipher": {
      "predicted_class": "caesar",
      "confidence": 0.92
    }
  },
  "extracted_features": {
    "entropy": 4.12,
    "ioc": 0.051,
    "...": "..."
  }
}
```

## 5. Enhancements & Recommendations (To Improve the Model from Current Research)
To elevate the research model into a robust production system, the following enhancements are required:

### 5.1 Model & Feature Enhancements
*   **N-gram Frequency Cosine Similarity:** Compare ciphertext bigram/trigram frequencies against standard English corpus frequencies. Monoalphabetic ciphers retain identical frequency structures (just shifted), which drastically improves separation from Modern/Polygraphic ciphers.
*   **Kasiski Examination / Auto-correlation Feature:** Go beyond finding variance in IoC by identifying explicit repeating substrings to distinctly predict poly-alphabetic key lengths.
*   **Thresholding & "Unknown" Handling:** If Stage 1 or Stage 2 confidence drops below a threshold (e.g., `< 0.5`), the API should flag the prediction as `"low_confidence"` or return `"unknown"`. Real-world inputs might be encodings (like Base64) rather than ciphers.
*   **Shorter Ciphertext Handle:** The research generates plaintexts of lengths 200-800. The backend should handle "short strings" (e.g., <50 characters) gracefully, either by injecting a warning that statistical significance is low, or using a specialized few-shot model.

### 5.2 System & Infrastructure Enhancements
*   **Asynchronous Processing:** If feature extraction relies on expensive computations for huge texts, implement background jobs (e.g., Celery/Redis) giving a `task_id` rather than blocking the HTTP request.
*   **Ensemble Output:** Instead of returning only the top-1 cipher, return the **Top-3** possibilities with probabilities to give the analyst more options.
*   **Feedback Loop / Data Flywheel API:** Add an endpoint `POST /api/v1/feedback` where analysts can supply the true cipher type of a string. Save this in a database to continuously retrain and improve the model.
*   **Modularity:** Use a Factory Design Pattern in the Model Router. If a new cipher (e.g., AES) is added to the "Modern" family model, the codebase shouldn't require major refactoring.

## 6. Implementation Roadmap for AI Agents
If utilizing AI agents to build this, instruct them in the following sequence:
1.  **Agent 1 (Data Engineering):** Implement the Python Feature Extraction module exactly as matched in the Jupyter notebook. Include unit tests for edge cases (empty strings, non-ascii).
2.  **Agent 2 (ML Engineering):** Build a `ModelManager` class that abstracts loading scikit-learn/XGBoost `.pkl` or `.onnx` models and chaining inferences hierarchically.
3.  **Agent 3 (Backend Engineering):** Set up a FastAPI service. Connect the HTTP routes to the `ModelManager` and Feature Extractor. Implement input validation using Pydantic.
4.  **Agent 4 (Deployment):** Dockerize the application and set up a basic `docker-compose.yml` to serve the API.
