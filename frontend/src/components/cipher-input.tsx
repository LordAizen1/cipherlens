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
import { Eraser, FlaskConical, Loader2, Layers, BrainCircuit, GitBranch, Lightbulb, Info, ChevronDown, ChevronUp } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import { useState } from "react";

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

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [exampleKey, setExampleKey] = useState(0);
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
        confidence_threshold: 0.01,
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
            {charCount > 0 && charCount < 5 ? (
              <span className="text-destructive">Minimum 5 characters</span>
            ) : charCount >= 5 && charCount < 100 ? (
              <span className="text-yellow-600 dark:text-yellow-500">100+ chars recommended for best accuracy</span>
            ) : null}
          </div>
        </div>

        {/* Advanced: Model type selector */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            {showAdvanced ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            Advanced
            {modelType !== "hybrid" && (
              <span className="ml-1 rounded bg-muted px-1.5 py-0.5 text-[10px]">
                {modelType === "deep_learning" ? "CNN DL" : "XGBoost"}
              </span>
            )}
          </button>
          {showAdvanced && (
            <div className="mt-2 space-y-1.5">
              <div className="flex items-center gap-1.5">
                <label className="text-xs font-medium text-muted-foreground">Model Engine</label>
                <TooltipProvider delayDuration={200}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Info className="h-3 w-3 text-muted-foreground cursor-help" />
                    </TooltipTrigger>
                    <TooltipContent side="right" className="max-w-[280px] text-xs">
                      <p className="font-semibold mb-1">Choose a prediction model:</p>
                      <p><span className="font-medium">Hybrid CNN</span> — Combines raw character patterns with statistical features. Best overall accuracy.</p>
                      <p className="mt-1"><span className="font-medium">CNN Deep Learning</span> — Reads character sequences directly. Best for numeric ciphers like Polybius.</p>
                      <p className="mt-1"><span className="font-medium">XGBoost</span> — Uses statistical features with a two-stage family→cipher pipeline. Fast and interpretable.</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <Select value={modelType} onValueChange={(v) => setModelType(v as "hierarchical" | "deep_learning" | "hybrid")}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hybrid">
                    <div className="flex items-center gap-2">
                      <Layers className="h-3.5 w-3.5" />
                      Hybrid CNN
                      <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">Recommended</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="deep_learning">
                    <div className="flex items-center gap-2">
                      <BrainCircuit className="h-3.5 w-3.5" />
                      CNN Deep Learning
                    </div>
                  </SelectItem>
                  <SelectItem value="hierarchical">
                    <div className="flex items-center gap-2">
                      <GitBranch className="h-3.5 w-3.5" />
                      XGBoost
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        {/* Example selector */}
        <Select key={exampleKey} onValueChange={handleExample}>
          <SelectTrigger className="w-full">
            <div className="flex items-center gap-2">
              <Lightbulb className="h-3.5 w-3.5" />
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
              setExampleKey((k) => k + 1);
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

