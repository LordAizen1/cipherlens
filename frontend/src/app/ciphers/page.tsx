"use client";

import { useState } from "react";
import { CipherCard } from "@/components/cipher-card";
import { Badge } from "@/components/ui/badge";
import { CIPHER_DATA, CIPHER_FAMILIES } from "@/lib/constants";
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
          {CIPHER_FAMILIES.map((family, i) => {
            const colors = [
              "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400",
              "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400",
              "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400",
              "bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-400",
              "bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-400",
              "bg-cyan-100 text-cyan-700 dark:bg-cyan-950 dark:text-cyan-400",
              "bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-400",
            ];
            const isActive = activeFamily === family.slug;
            return (
              <button
                key={family.slug}
                className={`inline-flex items-center rounded-md border border-transparent px-2.5 py-0.5 text-xs font-semibold transition-colors ${colors[i % colors.length]} ${isActive ? "ring-2 ring-offset-2 ring-offset-background ring-foreground/30" : "opacity-75 hover:opacity-100"}`}
                onClick={() =>
                  setActiveFamily(isActive ? null : family.slug)
                }
              >
                {family.name} ({family.count})
              </button>
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
