"use client";

import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { useCipherStore } from "@/hooks/use-cipher-store";
import { BarChart3, Activity, Hash, Sigma, Ruler, FileArchive, Shuffle, Binary, Repeat, TrendingUp, Percent, Info } from "lucide-react";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from "recharts";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
}

function fmt(value: number, decimals = 4): string {
  return parseFloat(value.toFixed(decimals)).toString();
}

function MetricCard({ icon, label, value, subtext }: MetricCardProps) {
  return (
    <div className="rounded-lg border p-3">
      <div className="mb-1 flex items-center gap-2 text-xs text-muted-foreground">
        {icon}
        {label}
      </div>
      <div className="truncate text-lg font-bold tabular-nums">{value}</div>
      {subtext && (
        <div className="truncate text-xs text-muted-foreground">{subtext}</div>
      )}
    </div>
  );
}

const radarChartConfig = {
  value: {
    label: "Value",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig;

export function FeatureProfile() {
  const { result, isAnalyzing } = useCipherStore();

  if (isAnalyzing) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Activity className="h-5 w-5" />
            Feature Profile
            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-3.5 w-3.5 cursor-help text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent side="right" className="max-w-[260px] text-xs">
                  A radar chart visualizing 8 key statistical properties of the ciphertext, normalized to a 0–100 scale for comparison across cipher types.
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="mx-auto h-[300px] w-[300px]" />
        </CardContent>
      </Card>
    );
  }

  if (!result) return null;

  const { features } = result;

  const maxEntropy = 8;
  const radarData = [
    { feature: "Entropy",      value: Math.min((features.entropy / maxEntropy) * 100, 100) },
    { feature: "IoC",          value: Math.min(features.ioc * 1000, 100) },
    { feature: "Bigram Ent.",  value: Math.min((features.bigram_entropy / 15) * 100, 100) },
    { feature: "Trigram Ent.", value: Math.min((features.trigram_entropy / 20) * 100, 100) },
    { feature: "Uniformity",   value: Math.min((features.uniformity / 10) * 100, 100) },
    { feature: "Compression",  value: features.compression * 100 },
    { feature: "Symbol Ratio", value: features.unique_ratio * 100 },
    { feature: "Trans. Var.",  value: Math.min((features.transition_var / 500) * 100, 100) },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.3 }}
    >
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Activity className="h-5 w-5" />
            Feature Profile
            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-3.5 w-3.5 cursor-help text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent side="right" className="max-w-[260px] text-xs">
                  A radar chart visualizing 8 key statistical properties of the ciphertext, normalized to a 0–100 scale for comparison across cipher types.
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={radarChartConfig} className="mx-auto aspect-square h-[300px]">
            <RadarChart data={radarData}>
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis
                dataKey="feature"
                tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={false}
                axisLine={false}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Radar
                name="value"
                dataKey="value"
                stroke="hsl(var(--chart-2))"
                fill="hsl(var(--chart-2))"
                fillOpacity={0.3}
                strokeWidth={2}
              />
            </RadarChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function FeatureAnalysis() {
  const { result, isAnalyzing } = useCipherStore();

  if (isAnalyzing) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <BarChart3 className="h-5 w-5" />
            Feature Analysis
            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-3.5 w-3.5 cursor-help text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent side="right" className="max-w-[260px] text-xs">
                  The 15 statistical features extracted from your ciphertext. These are the raw values the model uses to distinguish between cipher types.
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {Array.from({ length: 13 }).map((_, i) => (
              <Skeleton key={i} className="h-20" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!result) return null;

  const { features } = result;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.3 }}
    >
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <BarChart3 className="h-5 w-5" />
            Feature Analysis
            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-3.5 w-3.5 cursor-help text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent side="right" className="max-w-[260px] text-xs">
                  The 15 statistical features extracted from your ciphertext. These are the raw values the model uses to distinguish between cipher types.
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <MetricCard icon={<Ruler className="h-3 w-3" />} label="Length" value={features.length} subtext="characters" />
            <MetricCard icon={<Activity className="h-3 w-3" />} label="Shannon Entropy" value={fmt(features.entropy)} subtext="bits/char" />
            <MetricCard icon={<FileArchive className="h-3 w-3" />} label="Compression Ratio" value={fmt(features.compression)} subtext="compressed / original" />
            <MetricCard icon={<Binary className="h-3 w-3" />} label="Bigram Entropy" value={fmt(features.bigram_entropy)} subtext="bits/bigram" />
            <MetricCard icon={<Binary className="h-3 w-3" />} label="Trigram Entropy" value={fmt(features.trigram_entropy)} subtext="bits/trigram" />
            <MetricCard icon={<Sigma className="h-3 w-3" />} label="Uniformity" value={fmt(features.uniformity)} subtext="freq std dev" />
            <MetricCard icon={<Percent className="h-3 w-3" />} label="Unique Symbol Ratio" value={fmt(features.unique_ratio)} subtext="unique / total" />
            <MetricCard icon={<Shuffle className="h-3 w-3" />} label="Transition Variance" value={typeof features.transition_var === "number" ? features.transition_var.toFixed(2) : features.transition_var} subtext="char-to-char" />
            <MetricCard icon={<Repeat className="h-3 w-3" />} label="Run-Length Mean" value={typeof features.run_length_mean === "number" ? features.run_length_mean.toFixed(2) : features.run_length_mean} />
            <MetricCard icon={<Repeat className="h-3 w-3" />} label="Run-Length Variance" value={typeof features.run_length_var === "number" ? features.run_length_var.toFixed(4) : features.run_length_var} />
            <MetricCard icon={<Hash className="h-3 w-3" />} label="Index of Coincidence" value={fmt(features.ioc, 6)} subtext={features.ioc > 0.06 ? "≈ monoalphabetic" : "≈ polyalphabetic"} />
            <MetricCard icon={<TrendingUp className="h-3 w-3" />} label="IoC Variance" value={fmt(features.ioc_variance, 6)} subtext="periodicity measure" />
            <MetricCard icon={<TrendingUp className="h-3 w-3" />} label="Kasiski IoC" value={fmt(features.max_kasiski_ioc, 6)} subtext={features.max_kasiski_ioc > 0.055 ? "periodic structure" : "no periodicity"} />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
