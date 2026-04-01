"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCipherStore } from "@/hooks/use-cipher-store";
import { Zap, Info } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

const title = (
  <CardTitle className="flex items-center gap-2 text-lg">
    <Zap className="h-5 w-5" />
    Feature Importance
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Info className="h-3.5 w-3.5 cursor-help text-muted-foreground" />
        </TooltipTrigger>
        <TooltipContent side="right" className="max-w-[260px] text-xs">
          Shows which statistical features the model relied on most when making its prediction. Higher bars mean that feature had more influence on the result.
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  </CardTitle>
);

export function FeatureImportanceCard() {
  const { result, isAnalyzing } = useCipherStore();

  if (isAnalyzing) {
    return (
      <Card>
        <CardHeader className="pb-3">
          {title}
        </CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-6 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (!result) return null;

  const { feature_importance, model_used } = result;

  if (!feature_importance || feature_importance.length === 0) {
    return (
      <Card>
        <CardHeader className="pb-3">
          {title}
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Not available for the <span className="font-medium">{model_used}</span> model.
          </p>
        </CardContent>
      </Card>
    );
  }

  const sorted = [...feature_importance].sort((a, b) => b.importance_score - a.importance_score);
  const max = sorted[0].importance_score;

  const FEATURE_LABELS: Record<string, string> = {
    length:           "Length",
    entropy:          "Shannon Entropy",
    compression:      "Compression Ratio",
    bigram_entropy:   "Bigram Entropy",
    trigram_entropy:  "Trigram Entropy",
    uniformity:       "Uniformity",
    unique_ratio:     "Unique Symbol Ratio",
    transition_var:   "Transition Variance",
    run_length_mean:  "Run-Length Mean",
    run_length_var:   "Run-Length Variance",
    ioc:              "Index of Coincidence",
    ioc_variance:     "IoC Variance",
    digit_ratio:      "Digit Ratio",
    alpha_ratio:      "Alpha Ratio",
    max_kasiski_ioc:  "Kasiski IoC",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.3 }}
    >
      <Card>
        <CardHeader className="pb-3">
          {title}
        </CardHeader>
        <CardContent className="space-y-1.5">
          {sorted.map((f, i) => {
            const pct = (f.importance_score / max) * 100;
            const label = FEATURE_LABELS[f.feature_name] ?? f.feature_name;
            return (
              <div key={f.feature_name} className="flex items-center gap-2">
                <span className="w-36 shrink-0 text-right text-xs text-muted-foreground truncate">
                  {label}
                </span>
                <div className="relative h-5 flex-1 overflow-hidden rounded bg-muted">
                  <motion.div
                    className="h-full rounded bg-chart-1"
                    style={{ opacity: i === 0 ? 0.9 : 0.5 - i * 0.02 > 0.2 ? 0.5 - i * 0.02 : 0.2 }}
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.5, delay: i * 0.04, ease: "easeOut" }}
                  />
                </div>
                <span className="w-10 shrink-0 text-right text-xs tabular-nums text-muted-foreground">
                  {(f.importance_score * 100).toFixed(1)}%
                </span>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </motion.div>
  );
}
