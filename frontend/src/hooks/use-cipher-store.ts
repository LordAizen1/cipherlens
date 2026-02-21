import { create } from "zustand";
import { PredictionResponse } from "@/lib/types";

interface CipherStore {
  ciphertext: string;
  setCiphertext: (text: string) => void;
  modelType: "hierarchical" | "unified";
  setModelType: (type: "hierarchical" | "unified") => void;
  confidenceThreshold: number;
  setConfidenceThreshold: (threshold: number) => void;
  showFeatures: boolean;
  setShowFeatures: (show: boolean) => void;
  result: PredictionResponse | null;
  setResult: (result: PredictionResponse | null) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (analyzing: boolean) => void;
}

export const useCipherStore = create<CipherStore>((set) => ({
  ciphertext: "",
  setCiphertext: (text) => set({ ciphertext: text }),
  modelType: "hierarchical",
  setModelType: (type) => set({ modelType: type }),
  confidenceThreshold: 0.6,
  setConfidenceThreshold: (threshold) => set({ confidenceThreshold: threshold }),
  showFeatures: true,
  setShowFeatures: (show) => set({ showFeatures: show }),
  result: null,
  setResult: (result) => set({ result }),
  isAnalyzing: false,
  setIsAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),
}));
