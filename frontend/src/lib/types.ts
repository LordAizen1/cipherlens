// API Contract Types — matches the backend PredictionRequest/Response

export interface PredictionRequest {
  ciphertext: string;
  model_type: "hierarchical" | "unified" | "deep_learning" | "hybrid";
  confidence_threshold: number;
  include_features: boolean;
}

export interface CipherPrediction {
  cipher_name: string;
  cipher_family: string;
  confidence: number;
}

export interface FeatureSet {
  entropy: number;
  ioc: number;
  chi_square: number;
  alphabet_size: number;
  has_spaces: boolean;
  digit_ratio: number;
  alpha_ratio: number;
  bigram_entropy: number;
  trigram_entropy: number;
  [key: string]: number | boolean | string;
}

export interface FeatureImportance {
  feature_name: string;
  importance_score: number;
}

export interface PredictionResponse {
  request_id: string;
  timestamp: string;
  top_prediction: CipherPrediction;
  all_predictions: CipherPrediction[];
  features: FeatureSet;
  feature_importance: FeatureImportance[];
  model_used: "hierarchical" | "unified" | "deep_learning" | "hybrid";
  inference_time_ms: number;
}

// Static cipher info for the encyclopedia
export interface CipherInfo {
  name: string;
  slug: string;
  family: string;
  familySlug: string;
  description: string;
  formula: string;
  blockSize: string;
  keySize: string;
  outputType: "Alphabetic" | "Numeric pairs" | "Hexadecimal" | "Limited alphabet";
  historicalNote: string;
  weaknesses: string[];
  example: {
    plaintext: string;
    key: string;
    ciphertext: string;
  };
}

export type CipherFamily =
  | "Monoalphabetic Substitution"
  | "Polyalphabetic Substitution"
  | "Transposition"
  | "Polygraphic Substitution"
  | "Fractionating"
  | "Modern Block"
  | "Numeric";

export const FAMILY_COLORS: Record<CipherFamily, string> = {
  "Monoalphabetic Substitution": "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  "Polyalphabetic Substitution": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  "Transposition": "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  "Polygraphic Substitution": "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
  "Fractionating": "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
  "Modern Block": "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400",
  "Numeric": "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
};
