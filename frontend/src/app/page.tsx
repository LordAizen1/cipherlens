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
        {/* Left — Input */}
        <div>
          <BlurFade delay={0.2}>
            <CipherInput />
          </BlurFade>
        </div>

        {/* Right — Results */}
        <div className="space-y-6">
          <BlurFade delay={0.3}>
            <PredictionResults />
          </BlurFade>
          <FeatureAnalysis />
          <CipherInfoCard />
        </div>
      </div>
    </div>
  );
}
