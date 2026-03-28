"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useCipherStore } from "@/hooks/use-cipher-store";
import { CIPHER_DATA } from "@/lib/constants";
import { BookOpen, AlertTriangle, Key, FileCode2 } from "lucide-react";
import { LaTeX } from "@/components/latex";

export function CipherInfoCard() {
  const { result } = useCipherStore();

  if (!result) return null;

  const cipher = CIPHER_DATA.find(
    (c) => c.slug === result.top_prediction.cipher_name
  );

  if (!cipher) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.35, duration: 0.3 }}
    >
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <BookOpen className="h-5 w-5" />
            About {cipher.name} Cipher
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">{cipher.description}</p>

          {/* Formula */}
          <div className="rounded-md bg-muted p-3">
            <div className="mb-1 flex items-center gap-2 text-xs font-medium">
              <FileCode2 className="h-3 w-3" />
              Formula
            </div>
            <LaTeX math={cipher.formula} className="text-sm" />
          </div>

          {/* Details grid */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-muted-foreground">Block size:</span>{" "}
              <span className="font-medium">{cipher.blockSize}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Key size:</span>{" "}
              <span className="font-medium">{cipher.keySize}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Output:</span>{" "}
              <span className="font-medium">{cipher.outputType}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Family:</span>{" "}
              <span className="font-medium">{cipher.family}</span>
            </div>
          </div>

          {/* Historical note */}
          <div className="text-sm italic text-muted-foreground">
            {cipher.historicalNote}
          </div>

          {/* Weaknesses */}
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-medium">
              <AlertTriangle className="h-3 w-3" />
              Known Weaknesses
            </div>
            <div className="flex flex-wrap gap-1.5">
              {cipher.weaknesses.map((w) => (
                <Badge key={w} variant="outline" className="text-xs">
                  {w}
                </Badge>
              ))}
            </div>
          </div>

          {/* Example */}
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-medium">
              <Key className="h-3 w-3" />
              Example
            </div>
            <div className="space-y-1 rounded-md bg-muted p-3 font-mono text-xs">
              <div>
                <span className="text-muted-foreground">Plaintext: </span>
                {cipher.example.plaintext}
              </div>
              <div>
                <span className="text-muted-foreground">Key: </span>
                {cipher.example.key}
              </div>
              <div>
                <span className="text-muted-foreground">Ciphertext: </span>
                {cipher.example.ciphertext}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
