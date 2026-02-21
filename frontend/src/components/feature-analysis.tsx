"use client";

import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCipherStore } from "@/hooks/use-cipher-store";
import { BarChart3, Activity, Hash, Type, Sigma } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const CHART_COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
];

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
          <div className="grid grid-cols-2 gap-3">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </div>
          <Skeleton className="h-48" />
        </CardContent>
      </Card>
    );
  }

  if (!result) return null;

  const { features, feature_importance } = result;

  const chartData = feature_importance.map((f) => ({
    name: f.feature_name.replace("_", " "),
    value: parseFloat((f.importance_score * 100).toFixed(1)),
  }));

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
        <CardContent className="space-y-4">
          {/* Key metrics */}
          <div className="grid grid-cols-2 gap-3">
            <MetricCard
              icon={<Activity className="h-3 w-3" />}
              label="Shannon Entropy"
              value={features.entropy}
              subtext="bits/char"
            />
            <MetricCard
              icon={<Hash className="h-3 w-3" />}
              label="Index of Coincidence"
              value={features.ioc}
              subtext={features.ioc > 0.06 ? "≈ monoalphabetic" : "≈ polyalphabetic"}
            />
            <MetricCard
              icon={<Sigma className="h-3 w-3" />}
              label="Chi-Square"
              value={features.chi_square}
            />
            <MetricCard
              icon={<Type className="h-3 w-3" />}
              label="Alphabet Size"
              value={features.alphabet_size}
              subtext={`${(features.alpha_ratio * 100).toFixed(0)}% alpha, ${(features.digit_ratio * 100).toFixed(0)}% digits`}
            />
          </div>

          {/* Feature importance chart */}
          <div>
            <h4 className="mb-2 text-sm font-medium">Feature Importance</h4>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  layout="vertical"
                  margin={{ left: 0, right: 10, top: 5, bottom: 5 }}
                >
                  <XAxis type="number" hide />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={120}
                    tick={{ fontSize: 11, fill: "hsl(var(--foreground))" }}
                  />
                  <Tooltip
                    formatter={(value) => `${value}%`}
                    contentStyle={{
                      borderRadius: "8px",
                      border: "1px solid hsl(var(--border))",
                      backgroundColor: "hsl(var(--card))",
                      color: "hsl(var(--foreground))",
                    }}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {chartData.map((_, i) => (
                      <Cell
                        key={i}
                        fill={CHART_COLORS[i % CHART_COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
