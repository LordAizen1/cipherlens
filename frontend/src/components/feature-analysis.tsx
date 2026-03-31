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
import { BarChart3, Activity, Hash, Sigma, Ruler, FileArchive, Shuffle, Binary, Repeat, TrendingUp, Percent } from "lucide-react";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from "recharts";

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
}

function MetricCard({ icon, label, value, subtext }: MetricCardProps) {
  return (
    <div className="rounded-lg border p-3">
      <div className="mb-1 flex items-center gap-2 text-xs text-muted-foreground">
        {icon}
        {label}
      </div>
      <div className="text-xl font-bold tabular-nums">{value}</div>
      {subtext && (
        <div className="text-xs text-muted-foreground">{subtext}</div>
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

export function FeatureAnalysis() {
  const { result, isAnalyzing } = useCipherStore();

  if (isAnalyzing) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <BarChart3 className="h-5 w-5" />
            Feature Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {Array.from({ length: 12 }).map((_, i) => (
              <Skeleton key={i} className="h-20" />
            ))}
          </div>
          <Skeleton className="h-48" />
        </CardContent>
      </Card>
    );
  }

  if (!result) return null;

  const { features } = result;

  // Normalize features for radar chart (0–100 scale)
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
            <BarChart3 className="h-5 w-5" />
            Feature Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Key metrics — 12 PRD features */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <MetricCard
              icon={<Ruler className="h-3 w-3" />}
              label="Length"
              value={features.length}
              subtext="characters"
            />
            <MetricCard
              icon={<Activity className="h-3 w-3" />}
              label="Shannon Entropy"
              value={features.entropy}
              subtext="bits/char"
            />
            <MetricCard
              icon={<FileArchive className="h-3 w-3" />}
              label="Compression Ratio"
              value={features.compression}
              subtext="compressed / original"
            />
            <MetricCard
              icon={<Binary className="h-3 w-3" />}
              label="Bigram Entropy"
              value={features.bigram_entropy}
              subtext="bits/bigram"
            />
            <MetricCard
              icon={<Binary className="h-3 w-3" />}
              label="Trigram Entropy"
              value={features.trigram_entropy}
              subtext="bits/trigram"
            />
            <MetricCard
              icon={<Sigma className="h-3 w-3" />}
              label="Uniformity"
              value={features.uniformity}
              subtext="freq std dev"
            />
            <MetricCard
              icon={<Percent className="h-3 w-3" />}
              label="Unique Symbol Ratio"
              value={features.unique_ratio}
              subtext="unique / total"
            />
            <MetricCard
              icon={<Shuffle className="h-3 w-3" />}
              label="Transition Variance"
              value={typeof features.transition_var === "number" ? features.transition_var.toFixed(2) : features.transition_var}
              subtext="char-to-char"
            />
            <MetricCard
              icon={<Repeat className="h-3 w-3" />}
              label="Run-Length Mean"
              value={typeof features.run_length_mean === "number" ? features.run_length_mean.toFixed(2) : features.run_length_mean}
            />
            <MetricCard
              icon={<Repeat className="h-3 w-3" />}
              label="Run-Length Variance"
              value={typeof features.run_length_var === "number" ? features.run_length_var.toFixed(4) : features.run_length_var}
            />
            <MetricCard
              icon={<Hash className="h-3 w-3" />}
              label="Index of Coincidence"
              value={features.ioc}
              subtext={features.ioc > 0.06 ? "≈ monoalphabetic" : "≈ polyalphabetic"}
            />
            <MetricCard
              icon={<TrendingUp className="h-3 w-3" />}
              label="IoC Variance"
              value={features.ioc_variance}
              subtext="periodicity measure"
            />
          </div>

          {/* Radar chart — feature profile */}
          <div>
            <h4 className="mb-2 text-sm font-medium">Feature Profile</h4>
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
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
