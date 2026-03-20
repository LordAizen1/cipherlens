import { Github } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t py-4">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 text-sm text-muted-foreground">
        <p>CipherLens &middot; IIIT Delhi</p>
        <a
          href="https://github.com/LordAizen1/cipherlens"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 transition-colors hover:text-foreground"
        >
          <Github className="h-4 w-4" />
          GitHub
        </a>
      </div>
    </footer>
  );
}
