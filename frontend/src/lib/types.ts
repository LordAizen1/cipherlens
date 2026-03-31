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
  length: number;
  entropy: number;
  compression: number;        // backend field name
  bigram_entropy: number;
  trigram_entropy: number;
  uniformity: number;
  unique_ratio: number;       // backend field name
  transition_var: number;     // backend field name
  run_length_mean: number;
  run_length_var: number;     // backend field name
  ioc: number;
  ioc_variance: number;
  [key: string]: number | boolean | string;
}

export interface FeatureImportance {
  feature_name: string;
  importance_score: number;
}

export interface FamilyPrediction {
  predicted_family: string;
  confidence: number;
}

export interface PredictionResponse {
  request_id: string;
  timestamp: string;
  family_prediction?: FamilyPrediction;  // optional — not all models return this
  top_prediction: CipherPrediction;
  all_predictions: CipherPrediction[];
  features: FeatureSet;
  feature_importance: FeatureImportance[];
  model_used: "hierarchical" | "unified" | "deep_learning" | "hybrid";
  inference_time_ms: number;
  low_confidence?: boolean;  // optional
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
  "Monoalphabetic Substitution": "bg-red-200 text-red-900 dark:bg-red-900/60 dark:text-red-300",
  "Polyalphabetic Substitution": "bg-blue-200 text-blue-900 dark:bg-blue-900/60 dark:text-blue-300",
  "Transposition": "bg-green-200 text-green-900 dark:bg-green-900/60 dark:text-green-300",
  "Polygraphic Substitution": "bg-purple-200 text-purple-900 dark:bg-purple-900/60 dark:text-purple-300",
  "Fractionating": "bg-orange-200 text-orange-900 dark:bg-orange-900/60 dark:text-orange-300",
  "Modern Block": "bg-cyan-200 text-cyan-900 dark:bg-cyan-900/60 dark:text-cyan-300",
  "Numeric": "bg-yellow-200 text-yellow-900 dark:bg-yellow-900/60 dark:text-yellow-300",
};

// Maps short family names returned by the backend model to full display names
export const FAMILY_NAME_MAP: Record<string, CipherFamily> = {
  "mono":          "Monoalphabetic Substitution",
  "poly":          "Polyalphabetic Substitution",
  "transposition": "Transposition",
  "polygraphic":   "Polygraphic Substitution",
  "fractionating": "Fractionating",
  "modern":        "Modern Block",
  "numeric":       "Numeric",
};
