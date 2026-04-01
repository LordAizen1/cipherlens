"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { ConfidenceBar } from "@/components/confidence-bar";
import { useCipherStore } from "@/hooks/use-cipher-store";
import { FAMILY_COLORS, FAMILY_NAME_MAP, type CipherFamily } from "@/lib/types";
import { Trophy, ListOrdered, Clock, Cpu, AlertTriangle, GitBranch } from "lucide-react";
import { MorphingText } from "@/components/ui/morphing-text";
import { NumberTicker } from "@/components/ui/number-ticker";

export function PredictionResults() {
  const { result, isAnalyzing } = useCipherStore();

  if (isAnalyzing) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Trophy className="h-5 w-5" />
            Results
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-8 w-2/3" />
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card className="flex h-full flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg text-muted-foreground">
            <Trophy className="h-5 w-5" />
            Results
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-1 items-center justify-center">
          <MorphingText
            texts={["Awaiting Ciphertext...", "Ready To Decode...", "Paste & Analyze...", "Identify The Cipher..."]}
            className="h-8 w-64 text-base font-medium text-muted-foreground whitespace-nowrap md:h-8 lg:text-base"
          />
        </CardContent>
      </Card>
    );
  }

  const { family_prediction, top_prediction, all_predictions, model_used, inference_time_ms } = result;
  const fullFamilyName = FAMILY_NAME_MAP[top_prediction.cipher_family] ?? top_prediction.cipher_family;
  const familyColor = FAMILY_COLORS[fullFamilyName as CipherFamily] || "";
  const lowConfidence = top_prediction.confidence < 0.6;
  const top3 = all_predictions.slice(0, 3);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={result.request_id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Trophy className="h-5 w-5" />
                Results
              </CardTitle>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Cpu className="h-3 w-3" />
                  {model_used}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {inference_time_ms}ms
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Low confidence warning */}
            {lowConfidence && (
              <div className="flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-3 text-sm text-yellow-700 dark:text-yellow-400">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                Low confidence — the model is unsure. Consider the top 3 predictions below, or try a longer input (100+ characters).
              </div>
            )}

            {/* Two-stage prediction */}
            <div className="space-y-3">
              {/* Stage 1: Family (only shown if backend returns it) */}
              {family_prediction && (
                <div className="rounded-lg border p-3">
                  <div className="mb-1 flex items-center gap-2 text-xs text-muted-foreground">
                    <GitBranch className="h-3 w-3" />
                    Stage 1 — Family Classification
                  </div>
                  <div className="flex items-center justify-between">
                    <Badge className={familyColor} variant="secondary">
                      {FAMILY_NAME_MAP[family_prediction.predicted_family] ?? family_prediction.predicted_family}
                    </Badge>
                    <span className="text-sm font-bold tabular-nums">
                      {Math.round(family_prediction.confidence * 100)}%
                    </span>
                  </div>
                  <ConfidenceBar confidence={family_prediction.confidence} size="sm" showLabel={false} className="mt-2" />
                </div>
              )}

              {/* Stage 2: Cipher */}
              <div className="rounded-lg border bg-accent/30 p-4">
                <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
                  <Trophy className="h-3 w-3" />
                  Stage 2 — Cipher Identification
                </div>
                <div className="flex items-center justify-between">
                  <h3 className="text-2xl font-bold">{top_prediction.cipher_name}</h3>
                  <div className="text-right">
                    <div className="text-3xl font-bold tabular-nums">
                      <NumberTicker
                        value={Math.round(top_prediction.confidence * 100)}
                        className="text-3xl font-bold"
                      />
                      <span className="text-lg text-muted-foreground">%</span>
                    </div>
                    <span className="text-xs text-muted-foreground">confidence</span>
                  </div>
                </div>
                <ConfidenceBar confidence={top_prediction.confidence} size="lg" showLabel={false} />
              </div>
            </div>

            <Separator />

            {/* Top 3 predictions */}
            <div>
              <h4 className="mb-3 flex items-center gap-2 text-sm font-medium">
                <ListOrdered className="h-4 w-4" />
                Top Predictions
              </h4>
              <div className="space-y-2">
                {top3.map((pred, i) => {
                  const predFamily = FAMILY_NAME_MAP[pred.cipher_family] ?? pred.cipher_family;
                  const predColor = FAMILY_COLORS[predFamily as CipherFamily] || "";
                  return (
                    <motion.div
                      key={pred.cipher_name}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-center gap-3"
                    >
                      <span className="w-5 text-xs font-medium text-muted-foreground">
                        {i + 1}.
                      </span>
                      <span className="w-24 truncate text-sm font-medium">
                        {pred.cipher_name}
                      </span>
                      <div className="w-36 shrink-0">
                        <Badge className={`${predColor} text-[10px] px-1.5 py-0`} variant="secondary">
                          {predFamily}
                        </Badge>
                      </div>
                      <ConfidenceBar
                        confidence={pred.confidence}
                        className="flex-1"
                        size="sm"
                      />
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Remaining predictions (collapsed) */}
            {all_predictions.length > 3 && (
              <details className="group">
                <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground transition-colors">
                  Show all {all_predictions.length} predictions
                </summary>
                <div className="mt-2 space-y-1.5">
                  {all_predictions.slice(3).map((pred, i) => (
                    <div key={pred.cipher_name} className="flex items-center gap-3">
                      <span className="w-5 text-xs font-medium text-muted-foreground">
                        {i + 4}.
                      </span>
                      <span className="w-24 truncate text-xs text-muted-foreground">
                        {pred.cipher_name}
                      </span>
                      <ConfidenceBar
                        confidence={pred.confidence}
                        className="flex-1"
                        size="sm"
                      />
                    </div>
                  ))}
                </div>
              </details>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
}
