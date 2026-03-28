"use client";

import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCipherStore } from "@/hooks/use-cipher-store";
import { predictCipher } from "@/lib/api";
import { EXAMPLE_CIPHERTEXTS } from "@/lib/constants";
import { Eraser, FlaskConical, Loader2, Sparkles, Brain, Cpu } from "lucide-react";
import { toast } from "sonner";

export function CipherInput() {
  const {
    ciphertext,
    setCiphertext,
    modelType,
    setModelType,
    isAnalyzing,
    setIsAnalyzing,
    setResult,
  } = useCipherStore();

  const charCount = ciphertext.replace(/\s/g, "").length;

  async function handleAnalyze() {
    if (charCount < 5) {
      toast.error("Please enter at least 5 characters of ciphertext.");
      return;
    }

    setIsAnalyzing(true);
    setResult(null);

    try {
      const result = await predictCipher({
        ciphertext,
        model_type: modelType,
        confidence_threshold: 0.05,
        include_features: true,
      });
      setResult(result);
      const modelLabel = modelType === "hybrid" ? "Hybrid CNN" : modelType === "deep_learning" ? "CNN Deep Learning" : "XGBoost";
      toast.success(`Analysis complete using ${modelLabel} model`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to analyze ciphertext.";
      toast.error(message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  function handleExample(value: string) {
    const example = EXAMPLE_CIPHERTEXTS.find((e) => e.label === value);
    if (example) {
      setCiphertext(example.ciphertext);
      setResult(null);
    }
  }

  const modelIcon = modelType === "hybrid" ? <Sparkles className="h-3.5 w-3.5" /> : modelType === "deep_learning" ? <Brain className="h-3.5 w-3.5" /> : <Cpu className="h-3.5 w-3.5" />;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <FlaskConical className="h-5 w-5" />
          Analyze Ciphertext
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Textarea
            placeholder="Paste your ciphertext here..."
            className="min-h-[160px] resize-y font-mono text-sm"
            value={ciphertext}
            onChange={(e) => setCiphertext(e.target.value)}
          />
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{charCount} characters</span>
            {charCount > 0 && charCount < 5 && (
              <span className="text-destructive">Minimum 5 characters</span>
            )}
          </div>
        </div>

        {/* Model type selector */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground">Model Engine</label>
          <Select value={modelType} onValueChange={(v) => setModelType(v as "hierarchical" | "deep_learning" | "hybrid")}>
            <SelectTrigger className="w-full">
              <div className="flex items-center gap-2">
                {modelIcon}
                <SelectValue />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="hybrid">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-3.5 w-3.5" />
                  Hybrid CNN — Char + Features (87% acc) ✨
                </div>
              </SelectItem>
              <SelectItem value="deep_learning">
                <div className="flex items-center gap-2">
                  <Brain className="h-3.5 w-3.5" />
                  CNN Deep Learning (63% acc)
                </div>
              </SelectItem>
              <SelectItem value="hierarchical">
                <div className="flex items-center gap-2">
                  <Cpu className="h-3.5 w-3.5" />
                  XGBoost + Soft-Routing (76% acc)
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Example selector */}
        <Select onValueChange={handleExample}>
          <SelectTrigger className="w-full">
            <div className="flex items-center gap-2">
              <Sparkles className="h-3.5 w-3.5" />
              <SelectValue placeholder="Try an example..." />
            </div>
          </SelectTrigger>
          <SelectContent>
            {EXAMPLE_CIPHERTEXTS.map((example) => (
              <SelectItem key={example.label} value={example.label}>
                {example.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Action buttons */}
        <div className="flex gap-2">
          <Button
            className="flex-1"
            onClick={handleAnalyze}
            disabled={isAnalyzing || charCount < 5}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze"
            )}
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => {
              setCiphertext("");
              setResult(null);
            }}
            disabled={charCount === 0}
          >
            <Eraser className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

