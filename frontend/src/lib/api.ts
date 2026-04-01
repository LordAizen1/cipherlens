import { PredictionRequest, PredictionResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Strip spaces from ciphertext unless it looks like space-separated numbers
 *  (Nihilist / Polybius output: "36 27 48 55 ...")  */
function preprocessCiphertext(ct: string): string {
  const trimmed = ct.trim();
  const isNumeric = /^[\d\s]+$/.test(trimmed);
  return isNumeric ? trimmed : trimmed.replace(/\s+/g, "");
}

export async function predictCipher(
  request: PredictionRequest
): Promise<PredictionResponse> {
  const processed = { ...request, ciphertext: preprocessCiphertext(request.ciphertext) };
  const response = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(processed),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
