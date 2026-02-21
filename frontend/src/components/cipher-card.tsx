"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { CipherInfo, FAMILY_COLORS, type CipherFamily } from "@/lib/types";
import { Key, AlertTriangle, FileCode2 } from "lucide-react";

interface CipherCardProps {
  cipher: CipherInfo;
}

export function CipherCard({ cipher }: CipherCardProps) {
  const familyColor = FAMILY_COLORS[cipher.family as CipherFamily] || "";

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Card className="cursor-pointer transition-all hover:shadow-md hover:border-primary/30">
          <CardHeader className="pb-2">
            <div className="flex items-start justify-between">
              <CardTitle className="text-base">{cipher.name}</CardTitle>
              <Badge className={familyColor} variant="secondary">
                {cipher.familySlug}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="line-clamp-2 text-sm text-muted-foreground">
              {cipher.description}
            </p>
            <div className="mt-2 flex gap-2 text-xs text-muted-foreground">
              <span>Output: {cipher.outputType}</span>
            </div>
          </CardContent>
        </Card>
      </DialogTrigger>

      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {cipher.name} Cipher
            <Badge className={familyColor} variant="secondary">
              {cipher.family}
            </Badge>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">{cipher.description}</p>

          <div className="rounded-md bg-muted p-3">
            <div className="mb-1 flex items-center gap-2 text-xs font-medium">
              <FileCode2 className="h-3 w-3" />
              Formula
            </div>
            <code className="text-sm">{cipher.formula}</code>
          </div>

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
          </div>

          <div className="text-sm italic text-muted-foreground">
            {cipher.historicalNote}
          </div>

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
        </div>
      </DialogContent>
    </Dialog>
  );
}
