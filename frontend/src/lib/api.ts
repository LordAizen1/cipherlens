import { PredictionRequest, PredictionResponse } from "./types";
import { CIPHER_DATA } from "./constants";

// ── Mock API ──────────────────────────────────────────────────────────
// Simulates backend responses. When the FastAPI backend is ready,
// replace the body of predictCipher() with a real axios call:
//
//   import axios from "axios";
//   const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
//   return (await axios.post(`${API_BASE}/api/predict`, request)).data;

function randomBetween(min: number, max: number) {
  return Math.random() * (max - min) + min;
}

function generateMockPredictions(ciphertext: string) {
  // Simple heuristics to make mock predictions feel realistic
  const isNumericOnly = /^[\d\s]+$/.test(ciphertext);
  const isHex = /^[0-9A-Fa-f]+$/.test(ciphertext);
  const isADFGX = /^[ADFGXadfgx]+$/i.test(ciphertext);
  const isADFGVX = /^[ADFGVXadfgvx]+$/i.test(ciphertext);
  const hasSpaces = ciphertext.includes(" ");
  const uniqueChars = new Set(ciphertext.toUpperCase().replace(/\s/g, "")).size;

  let topCipher = "Vigenere";
  let topFamily = "Polyalphabetic Substitution";

  if (isNumericOnly && hasSpaces) {
    topCipher = "Nihilist";
    topFamily = "Fractionating";
  } else if (isNumericOnly) {
    topCipher = "Polybius Square";
    topFamily = "Numeric";
  } else if (isHex && ciphertext.length >= 16) {
    topCipher = "TEA";
    topFamily = "Modern Block";
  } else if (isADFGX && uniqueChars <= 5) {
    topCipher = "ADFGX";
    topFamily = "Fractionating";
  } else if (isADFGVX && uniqueChars <= 6) {
    topCipher = "ADFGVX";
    topFamily = "Fractionating";
  } else if (uniqueChars <= 20 && ciphertext.length > 10) {
    topCipher = "Caesar";
    topFamily = "Monoalphabetic Substitution";
  }

  // Build ranked predictions
  const allCiphers = CIPHER_DATA.map((c) => ({
    cipher_name: c.name,
    cipher_family: c.family,
    confidence: 0,
  }));

  // Assign confidence scores
  const topIdx = allCiphers.findIndex((c) => c.cipher_name === topCipher);
  if (topIdx !== -1) allCiphers[topIdx].confidence = randomBetween(0.78, 0.95);

  // Give same-family ciphers moderate confidence
  allCiphers.forEach((c, i) => {
    if (i !== topIdx && c.cipher_family === topFamily) {
      c.confidence = randomBetween(0.35, 0.72);
    } else if (c.confidence === 0) {
      c.confidence = randomBetween(0.01, 0.25);
    }
  });

  // Sort by confidence descending
  allCiphers.sort((a, b) => b.confidence - a.confidence);

  return allCiphers;
}

function generateMockFeatures(ciphertext: string) {
  const text = ciphertext.toUpperCase().replace(/\s/g, "");
  const len = text.length;

  // Compute real entropy
  const freq: Record<string, number> = {};
  for (const ch of text) freq[ch] = (freq[ch] || 0) + 1;
  let entropy = 0;
  for (const count of Object.values(freq)) {
    const p = count / len;
    entropy -= p * Math.log2(p);
  }

  // Compute real IoC
  let iocSum = 0;
  for (const count of Object.values(freq)) {
    iocSum += count * (count - 1);
  }
  const ioc = len > 1 ? iocSum / (len * (len - 1)) : 0;

  return {
    entropy: parseFloat(entropy.toFixed(4)),
    ioc: parseFloat(ioc.toFixed(6)),
    chi_square: parseFloat(randomBetween(50, 500).toFixed(2)),
    alphabet_size: new Set(text).size,
    has_spaces: ciphertext.includes(" "),
    digit_ratio: parseFloat(((text.match(/\d/g) || []).length / len).toFixed(4)),
    alpha_ratio: parseFloat(((text.match(/[A-Z]/g) || []).length / len).toFixed(4)),
    bigram_entropy: parseFloat(randomBetween(5, 10).toFixed(4)),
    trigram_entropy: parseFloat(randomBetween(7, 12).toFixed(4)),
  };
}

export async function predictCipher(
  request: PredictionRequest
): Promise<PredictionResponse> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700));

  const predictions = generateMockPredictions(request.ciphertext);
  const features = generateMockFeatures(request.ciphertext);

  const threshold = request.confidence_threshold;
  const filtered = predictions.filter((p) => p.confidence >= threshold);

  return {
    request_id: `pred_${Date.now().toString(36)}`,
    timestamp: new Date().toISOString(),
    top_prediction: predictions[0],
    all_predictions: filtered.length > 0 ? filtered : [predictions[0]],
    features,
    feature_importance: [
      { feature_name: "Index of Coincidence", importance_score: randomBetween(0.15, 0.35) },
      { feature_name: "Shannon Entropy", importance_score: randomBetween(0.1, 0.25) },
      { feature_name: "Chi-Square", importance_score: randomBetween(0.08, 0.2) },
      { feature_name: "Bigram Entropy", importance_score: randomBetween(0.05, 0.15) },
      { feature_name: "Alphabet Size", importance_score: randomBetween(0.04, 0.12) },
      { feature_name: "Digit Ratio", importance_score: randomBetween(0.02, 0.1) },
      { feature_name: "Trigram Entropy", importance_score: randomBetween(0.02, 0.08) },
      { feature_name: "Text Length", importance_score: randomBetween(0.01, 0.05) },
    ].sort((a, b) => b.importance_score - a.importance_score),
    model_used: request.model_type,
    inference_time_ms: Math.round(randomBetween(20, 120)),
  };
}
