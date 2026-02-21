"use client";

import katex from "katex";
import "katex/dist/katex.min.css";
import { useMemo } from "react";

interface LaTeXProps {
  math: string;
  className?: string;
}

function isLaTeX(str: string): boolean {
  return /[\\_{}\^]/.test(str);
}

export function LaTeX({ math, className }: LaTeXProps) {
  const html = useMemo(() => {
    if (!isLaTeX(math)) return null;
    try {
      return katex.renderToString(math, {
        throwOnError: false,
        displayMode: false,
      });
    } catch {
      return null;
    }
  }, [math]);

  if (!html) {
    return <code className={className}>{math}</code>;
  }

  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
