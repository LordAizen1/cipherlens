"use client";

import { useState } from "react";
import { CipherCard } from "@/components/cipher-card";
import { Badge } from "@/components/ui/badge";
import { CIPHER_DATA, CIPHER_FAMILIES } from "@/lib/constants";
import { FAMILY_COLORS, type CipherFamily } from "@/lib/types";
import { BlurFade } from "@/components/ui/blur-fade";

export default function CiphersPage() {
  const [activeFamily, setActiveFamily] = useState<string | null>(null);

  const filtered = activeFamily
    ? CIPHER_DATA.filter((c) => c.familySlug === activeFamily)
    : CIPHER_DATA;

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <BlurFade delay={0.1}>
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">
            Cipher Encyclopedia
          </h1>
          <p className="mt-1 text-muted-foreground">
            All 22 classical ciphers across 7 cryptographic families. Click any
            card to learn more.
          </p>
        </div>
      </BlurFade>

      {/* Family filter */}
      <BlurFade delay={0.2}>
        <div className="mb-6 flex flex-wrap gap-2">
          <Badge
            variant={activeFamily === null ? "default" : "outline"}
            className="cursor-pointer"
            onClick={() => setActiveFamily(null)}
          >
            All ({CIPHER_DATA.length})
          </Badge>
          {CIPHER_FAMILIES.map((family) => {
            const color =
              FAMILY_COLORS[family.name as CipherFamily] || "";
            return (
              <Badge
                key={family.slug}
                variant={activeFamily === family.slug ? "default" : "secondary"}
                className={`cursor-pointer ${activeFamily === family.slug ? "" : color}`}
                onClick={() =>
                  setActiveFamily(
                    activeFamily === family.slug ? null : family.slug
                  )
                }
              >
                {family.name} ({family.count})
              </Badge>
            );
          })}
        </div>
      </BlurFade>

      {/* Cipher grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((cipher, i) => (
          <BlurFade key={cipher.name} delay={0.05 * i}>
            <CipherCard cipher={cipher} />
          </BlurFade>
        ))}
      </div>
    </div>
  );
}
