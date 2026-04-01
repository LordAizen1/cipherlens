"use client";

import { CipherInput } from "@/components/cipher-input";
import { PredictionResults } from "@/components/prediction-results";
import { FeatureAnalysis, FeatureProfile } from "@/components/feature-analysis";
import { FeatureImportanceCard } from "@/components/feature-importance";
import { CipherInfoCard } from "@/components/cipher-info-card";
import { BlurFade } from "@/components/ui/blur-fade";
import { useCipherStore } from "@/hooks/use-cipher-store";

export default function Home() {
  const { result } = useCipherStore();
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
        <BlurFade delay={0.2}>
          <div className="flex flex-col gap-4">
            <CipherInput />
            <FeatureProfile />
            <CipherInfoCard />
          </div>
        </BlurFade>
        <BlurFade delay={0.3} className="h-full">
          <div className="flex h-full flex-col gap-4">
            <div className={result ? "" : "min-h-[400px] flex-1"}>
              <PredictionResults />
            </div>
            <FeatureAnalysis />
            <FeatureImportanceCard />
          </div>
        </BlurFade>
      </div>
    </div>
  );
}
