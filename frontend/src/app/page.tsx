"use client";

import { CipherInput } from "@/components/cipher-input";
import { PredictionResults } from "@/components/prediction-results";
import { FeatureAnalysis } from "@/components/feature-analysis";
import { CipherInfoCard } from "@/components/cipher-info-card";
import { BlurFade } from "@/components/ui/blur-fade";

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <BlurFade delay={0.1}>
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">
            Classical Cipher Identification
          </h1>
          <p className="mt-1 text-muted-foreground">
            Paste ciphertext below and let our ML models identify the encryption
            algorithm used. Supports 22 cipher types across 7 cryptographic
            families.
          </p>
        </div>
      </BlurFade>

      <div className="grid gap-6 lg:grid-cols-[400px_1fr]">
        {/* Row 1: Input + Results (same height) */}
        <BlurFade delay={0.2}>
          <CipherInput />
        </BlurFade>
        <BlurFade delay={0.3} className="h-full">
          <PredictionResults />
        </BlurFade>

        {/* Row 2+: Right-side only */}
        <div className="lg:col-start-2">
          <FeatureAnalysis />
        </div>
        <div className="lg:col-start-2">
          <CipherInfoCard />
        </div>
      </div>
    </div>
  );
}
