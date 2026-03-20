import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Brain,
  GitBranch,
  Users,
  Target,
  ArrowRight,
  Database,
  BarChart3,
  Cpu,
  Github,
} from "lucide-react";

const PIPELINE_STEPS = [
  { icon: <Database className="h-4 w-4" />, label: "Ciphertext Input", desc: "User pastes encrypted text" },
  { icon: <BarChart3 className="h-4 w-4" />, label: "Feature Extraction", desc: "31 statistical & structural features" },
  { icon: <GitBranch className="h-4 w-4" />, label: "Classification", desc: "Hierarchical or unified model" },
  { icon: <Target className="h-4 w-4" />, label: "Prediction", desc: "Ranked ciphers with confidence" },
];

const TEAM = [
  { name: "Dhruv Verma", roll: "2022172", github: "https://github.com/" },
  { name: "Maulik Mahey", roll: "2022282", github: "https://github.com/maulik-dot" },
  { name: "Md Kaif", roll: "2022289", github: "https://github.com/LordAizen1" },
  { name: "Sweta Snigdha", roll: "2022527", github: "https://github.com/cypherei00" },
];

const CIPHER_TABLE = [
  { family: "Monoalphabetic Substitution", ciphers: "Caesar, Affine, Atbash", count: 3 },
  { family: "Polyalphabetic Substitution", ciphers: "Vigenere, Autokey, Beaufort, Porta", count: 4 },
  { family: "Transposition", ciphers: "Columnar Transposition", count: 1 },
  { family: "Polygraphic Substitution", ciphers: "Playfair, Hill, Four-Square", count: 3 },
  { family: "Fractionating", ciphers: "Bifid, Trifid, ADFGX, ADFGVX, Nihilist", count: 5 },
  { family: "Modern Block", ciphers: "Lucifer, MISTY1, LOKI, TEA, XTEA", count: 5 },
  { family: "Numeric", ciphers: "Polybius Square", count: 1 },
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">
          About CipherLens
        </h1>
        <p className="mt-1 text-muted-foreground">
          A machine learning system for automated classical cipher
          identification.
        </p>
      </div>

      <div className="space-y-6">
        {/* Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Project Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>
              Classical cipher identification is the critical first step in any
              cryptanalysis workflow. Traditional manual methods are
              time-consuming and expertise-dependent.
            </p>
            <p>
              CipherLens automates this process using machine learning. Given
              only ciphertext (no plaintext or keys), our models extract 30+
              statistical features and classify the text into one of 22 cipher
              types across 7 cryptographic families — achieving up to 96%
              accuracy on distinct cipher families.
            </p>
            <p>
              The system uses a dual approach: a <strong>hierarchical
              classifier</strong> (family → specific cipher) and a{" "}
              <strong>unified classifier</strong> (single-stage multi-class),
              allowing performance comparison.
            </p>
          </CardContent>
        </Card>

        {/* Pipeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5" />
              How It Works
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-2">
              {PIPELINE_STEPS.map((step, i) => (
                <div key={step.label} className="flex items-center gap-2">
                  <div className="flex items-center gap-2 rounded-lg border p-3 text-sm">
                    {step.icon}
                    <div>
                      <div className="font-medium">{step.label}</div>
                      <div className="text-xs text-muted-foreground">
                        {step.desc}
                      </div>
                    </div>
                  </div>
                  {i < PIPELINE_STEPS.length - 1 && (
                    <ArrowRight className="hidden h-4 w-4 shrink-0 text-muted-foreground sm:block" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Cipher Taxonomy */}
        <Card>
          <CardHeader>
            <CardTitle>Supported Ciphers (22)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-2 pr-4 font-medium">Family</th>
                    <th className="pb-2 pr-4 font-medium">Ciphers</th>
                    <th className="pb-2 font-medium text-right">Count</th>
                  </tr>
                </thead>
                <tbody>
                  {CIPHER_TABLE.map((row) => (
                    <tr key={row.family} className="border-b last:border-0">
                      <td className="py-2 pr-4 font-medium">{row.family}</td>
                      <td className="py-2 pr-4 text-muted-foreground">
                        {row.ciphers}
                      </td>
                      <td className="py-2 text-right">
                        <Badge variant="secondary">{row.count}</Badge>
                      </td>
                    </tr>
                  ))}
                  <tr className="font-medium">
                    <td className="pt-2">Total</td>
                    <td />
                    <td className="pt-2 text-right">
                      <Badge>22</Badge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Separator />

        {/* Team */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Team
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {TEAM.map((member) => (
                <div key={member.roll} className="flex flex-col items-center gap-1 text-center">
                  <div className="flex items-center gap-1.5 text-sm font-medium">
                    <a
                      href={member.github}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground transition-colors hover:text-foreground"
                    >
                      <Github className="h-4 w-4" />
                    </a>
                    {member.name}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {member.roll}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 text-center text-sm text-muted-foreground">
              Supervised by <strong>Dr. Ravi Anand</strong> — IIIT Delhi
            </div>
            <div className="mt-1 text-center text-xs text-muted-foreground">
              BTP Spring 2026
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
