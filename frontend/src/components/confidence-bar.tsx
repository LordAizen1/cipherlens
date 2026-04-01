"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ConfidenceBarProps {
  confidence: number;
  className?: string;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
}

function getBarColor(confidence: number) {
  if (confidence >= 0.8) return "bg-green-600 dark:bg-green-500";
  if (confidence >= 0.6) return "bg-yellow-500 dark:bg-yellow-400";
  if (confidence >= 0.4) return "bg-orange-500 dark:bg-orange-400";
  return "bg-red-500 dark:bg-red-400";
}

export function ConfidenceBar({
  confidence,
  className,
  showLabel = true,
  size = "md",
}: ConfidenceBarProps) {
  const height = size === "sm" ? "h-1.5" : size === "md" ? "h-2.5" : "h-4";

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div
        className={cn(
          "flex-1 overflow-hidden rounded-full bg-secondary",
          height
        )}
      >
        <motion.div
          className={cn("h-full rounded-full", getBarColor(confidence))}
          initial={{ width: 0 }}
          animate={{ width: `${Math.round(confidence * 100)}%` }}
          transition={{ type: "spring", damping: 60, stiffness: 100 }}
        />
      </div>
      {showLabel && (
        <span className="min-w-[3rem] text-right text-sm font-medium tabular-nums">
          {(confidence * 100).toFixed(1)}%
        </span>
      )}
    </div>
  );
}
