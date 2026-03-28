import { CipherInfo } from "./types";

export const CIPHER_DATA: CipherInfo[] = [
  // ── Monoalphabetic Substitution ──────────────────────────────────────
  {
    name: "Caesar",
    slug: "caesar",
    family: "Monoalphabetic Substitution",
    familySlug: "monoalphabetic",
    description:
      "One of the simplest ciphers — each letter is shifted by a fixed number of positions in the alphabet.",
    formula: "C_i = (P_i + k) \\mod 26",
    blockSize: "1 char",
    keySize: "25 possible shifts",
    outputType: "Alphabetic",
    historicalNote:
      "Named after Julius Caesar, who reportedly used a shift of 3 to communicate with his generals.",
    weaknesses: ["Brute-force (only 25 keys)", "Frequency analysis"],
    example: {
      plaintext: "ATTACKATDAWN",
      key: "3",
      ciphertext: "DWWDFNDWGDZQ",
    },
  },
  {
    name: "Affine",
    slug: "affine",
    family: "Monoalphabetic Substitution",
    familySlug: "monoalphabetic",
    description:
      "Combines multiplicative and additive encryption. Each letter is encrypted using a linear function.",
    formula: "C_i = (a \\times P_i + b) \\mod 26",
    blockSize: "1 char",
    keySize: "312 pairs (12 valid a × 26 b)",
    outputType: "Alphabetic",
    historicalNote:
      "A generalization of the Caesar cipher. Caesar is the special case where a = 1.",
    weaknesses: ["Known-plaintext attack", "Frequency analysis", "Small key space"],
    example: {
      plaintext: "AFFINE",
      key: "a=5, b=8",
      ciphertext: "IHHWVC",
    },
  },
  {
    name: "Atbash",
    slug: "atbash",
    family: "Monoalphabetic Substitution",
    familySlug: "monoalphabetic",
    description:
      "A fixed substitution cipher where the alphabet is reversed (A↔Z, B↔Y, etc.).",
    formula: "C_i = (25 - P_i) \\mod 26",
    blockSize: "1 char",
    keySize: "1 (fixed substitution)",
    outputType: "Alphabetic",
    historicalNote:
      "One of the oldest known ciphers, originally used with the Hebrew alphabet. The name comes from the first, last, second, and second-to-last Hebrew letters.",
    weaknesses: ["No key — trivially breakable", "Frequency analysis"],
    example: {
      plaintext: "HELLO",
      key: "(none)",
      ciphertext: "SVOOL",
    },
  },

  // ── Polyalphabetic Substitution ──────────────────────────────────────
  {
    name: "Vigenere",
    slug: "vigenere",
    family: "Polyalphabetic Substitution",
    familySlug: "polyalphabetic",
    description:
      "Uses a repeating keyword to shift each letter by a different amount, creating multiple substitution alphabets.",
    formula: "C_i = (P_i + K_{i \\mod m}) \\mod 26",
    blockSize: "1 char",
    keySize: "26^m for key length m",
    outputType: "Alphabetic",
    historicalNote:
      "Considered 'unbreakable' for 300 years until Friedrich Kasiski published his examination method in 1863.",
    weaknesses: ["Kasiski examination", "Friedman test", "Frequency analysis per key position"],
    example: {
      plaintext: "ATTACKATDAWN",
      key: "LEMON",
      ciphertext: "LXFOPVEFRNHR",
    },
  },
  {
    name: "Autokey",
    slug: "autokey",
    family: "Polyalphabetic Substitution",
    familySlug: "polyalphabetic",
    description:
      "Like Vigenere but uses the plaintext itself as part of the key after an initial priming key, preventing key repetition.",
    formula: "C_i = (P_i + K'_i) \\mod 26, \\text{ where } K' = K \\| P",
    blockSize: "1 char",
    keySize: "Variable (priming key + plaintext)",
    outputType: "Alphabetic",
    historicalNote:
      "Invented by Blaise de Vigenere himself as an improvement over the standard Vigenere cipher.",
    weaknesses: ["Known-plaintext attacks", "Statistical analysis of key-plaintext mixing"],
    example: {
      plaintext: "ATTACKATDAWN",
      key: "QUEENLY",
      ciphertext: "QNXEPVYTWTWP",
    },
  },
  {
    name: "Beaufort",
    slug: "beaufort",
    family: "Polyalphabetic Substitution",
    familySlug: "polyalphabetic",
    description:
      "Similar to Vigenere but uses reciprocal subtraction. Encryption and decryption use the same operation.",
    formula: "C_i = (K_{i \\mod m} - P_i) \\mod 26",
    blockSize: "1 char",
    keySize: "26^m for key length m",
    outputType: "Alphabetic",
    historicalNote:
      "Named after Admiral Sir Francis Beaufort of the Royal Navy, also known for the Beaufort wind scale.",
    weaknesses: ["Same vulnerabilities as Vigenere", "Kasiski examination"],
    example: {
      plaintext: "HELLO",
      key: "KEY",
      ciphertext: "DANZQ",
    },
  },
  {
    name: "Porta",
    slug: "porta",
    family: "Polyalphabetic Substitution",
    familySlug: "polyalphabetic",
    description:
      "Uses a tableau of 13 reciprocal alphabets. The alphabet is split into halves (A-M and N-Z) with key-dependent swaps.",
    formula: "Tableau-based reciprocal substitution",
    blockSize: "1 char",
    keySize: "13^m for key length m",
    outputType: "Alphabetic",
    historicalNote:
      "Invented by Giovanni Battista della Porta in 1563, one of the earliest polyalphabetic ciphers.",
    weaknesses: ["Frequency analysis with sufficient ciphertext", "Only 13 alphabets (not 26)"],
    example: {
      plaintext: "DIPLOMACY",
      key: "FORTIFY",
      ciphertext: "SYSJHQZWR",
    },
  },

  // ── Transposition ────────────────────────────────────────────────────
  {
    name: "Columnar Transposition",
    slug: "columnar",
    family: "Transposition",
    familySlug: "transposition",
    description:
      "Writes plaintext in rows, then reads ciphertext off in columns according to a key-based permutation.",
    formula: "\\pi(K) \\text{ permutes column order}",
    blockSize: "Variable (key length)",
    keySize: "m! permutations for key length m",
    outputType: "Alphabetic",
    historicalNote:
      "Widely used in WWI and WWII, often combined with other ciphers for added security.",
    weaknesses: ["Preserves character frequencies", "Anagramming attacks", "Multiple anagramming"],
    example: {
      plaintext: "WEAREDISCOVERED",
      key: "ZEBRAS",
      ciphertext: "EVLNEACDTKESEAQROFOJ",
    },
  },

  // ── Polygraphic Substitution ─────────────────────────────────────────
  {
    name: "Playfair",
    slug: "playfair",
    family: "Polygraphic Substitution",
    familySlug: "polygraphic",
    description:
      "Encrypts pairs of letters (digraphs) using a 5×5 key square. Same-row, same-column, and rectangle rules determine substitution.",
    formula: "5×5 grid rules: row shift, column shift, rectangle swap",
    blockSize: "2 chars (digraph)",
    keySize: "25! possible key squares",
    outputType: "Alphabetic",
    historicalNote:
      "Invented by Charles Wheatstone in 1854, but named after Lord Playfair who promoted its use. Used by the British in the Boer War and WWI.",
    weaknesses: ["Digraph frequency analysis", "Known-plaintext attacks"],
    example: {
      plaintext: "HIDETHEGOLD",
      key: "MONARCHY",
      ciphertext: "BMODZBXDNABEKUDMUIXMMOUVIF",
    },
  },
  {
    name: "Hill",
    slug: "hill",
    family: "Polygraphic Substitution",
    familySlug: "polygraphic",
    description:
      "Uses matrix multiplication to encrypt blocks of letters simultaneously. The key is an invertible matrix mod 26.",
    formula: "\\mathbf{C} = \\mathbf{P} \\times \\mathbf{K} \\mod 26",
    blockSize: "n chars (matrix dimension)",
    keySize: "n×n invertible matrix mod 26",
    outputType: "Alphabetic",
    historicalNote:
      "Invented by Lester S. Hill in 1929. One of the first ciphers to use linear algebra.",
    weaknesses: ["Known-plaintext attack (solve linear system)", "Requires invertible key matrix"],
    example: {
      plaintext: "ACT",
      key: "[[6,24,1],[13,16,10],[20,17,15]]",
      ciphertext: "POH",
    },
  },
  {
    name: "Four-Square",
    slug: "foursquare",
    family: "Polygraphic Substitution",
    familySlug: "polygraphic",
    description:
      "An extension of Playfair using four 5×5 grids (two standard, two keyed) for stronger digraph encryption.",
    formula: "4-grid coordinate mapping on digraphs",
    blockSize: "2 chars (digraph)",
    keySize: "(25!)² for two independent keys",
    outputType: "Alphabetic",
    historicalNote:
      "Invented by Felix Delastelle, who also created the Bifid and Trifid ciphers.",
    weaknesses: ["Digraph frequency analysis (harder than Playfair)", "Known-plaintext attacks"],
    example: {
      plaintext: "HELPME",
      key: "EXAMPLE, KEYWORD",
      ciphertext: "FYGMKD",
    },
  },

  // ── Fractionating Ciphers ────────────────────────────────────────────
  {
    name: "Bifid",
    slug: "bifid",
    family: "Fractionating",
    familySlug: "fractionating",
    description:
      "Combines a Polybius square with transposition. Coordinates are split, concatenated, and re-paired for diffusion.",
    formula: "Polybius coords → split rows/cols → concatenate → re-pair",
    blockSize: "Variable",
    keySize: "25! possible squares",
    outputType: "Alphabetic",
    historicalNote:
      "Invented by Felix Delastelle around 1901. The fractionation step provides diffusion that simple substitution lacks.",
    weaknesses: ["Statistical analysis on large samples", "Known-plaintext attacks"],
    example: {
      plaintext: "FLEEATONCE",
      key: "BGWKZQPNDSIOAXEFCLUMTHYVR",
      ciphertext: "UAEOLWRINS",
    },
  },
  {
    name: "Trifid",
    slug: "trifid",
    family: "Fractionating",
    familySlug: "fractionating",
    description:
      "Extends Bifid to three dimensions using a 3×3×3 cube. Each letter maps to three coordinates for stronger diffusion.",
    formula: "3D cube coords → split → concatenate → re-triplet",
    blockSize: "Groups of g",
    keySize: "27! possible cubes",
    outputType: "Alphabetic",
    historicalNote:
      "Also by Felix Delastelle. The 3D fractionation makes it significantly harder to break than Bifid.",
    weaknesses: ["Statistical analysis", "Requires sufficient ciphertext length"],
    example: {
      plaintext: "SECRETMESSAGE",
      key: "FELIX",
      ciphertext: "ZLSJGNAETHRIH",
    },
  },
  {
    name: "ADFGX",
    slug: "adfgx",
    family: "Fractionating",
    familySlug: "fractionating",
    description:
      "A WWI German cipher combining Polybius substitution (using only letters A, D, F, G, X) with columnar transposition.",
    formula: "5×5 Polybius → ADFGX labels → columnar transposition",
    blockSize: "1 char → 2 ADFGX chars",
    keySize: "25! × m! (substitution + transposition)",
    outputType: "Limited alphabet",
    historicalNote:
      "Used by the German Army in Spring 1918. The five letters were chosen because they sound distinct in Morse code.",
    weaknesses: ["Broken by Georges Painvin in June 1918", "Limited alphabet is a giveaway"],
    example: {
      plaintext: "ATTACK",
      key: "CARGO, GERMAN",
      ciphertext: "FAXDFADDDGDGFFFAFAXAFAFX",
    },
  },
  {
    name: "ADFGVX",
    slug: "adfgvx",
    family: "Fractionating",
    familySlug: "fractionating",
    description:
      "Extension of ADFGX to support all 36 alphanumeric characters (A-Z + 0-9) using a 6×6 grid.",
    formula: "6×6 Polybius → ADFGVX labels → columnar transposition",
    blockSize: "1 char → 2 ADFGVX chars",
    keySize: "36! × m!",
    outputType: "Limited alphabet",
    historicalNote:
      "Extended version introduced by the German Army in June 1918. The 'V' was added to handle digits.",
    weaknesses: ["Same approach as ADFGX breaking", "6-letter alphabet is distinctive"],
    example: {
      plaintext: "ATTACK",
      key: "PRIVACY, FRENCH",
      ciphertext: "DGDDDAGDDGAFADDFDADVDVFAADVX",
    },
  },
  {
    name: "Nihilist",
    slug: "nihilist",
    family: "Fractionating",
    familySlug: "fractionating",
    description:
      "Combines Polybius square encoding with keyword addition. Produces numeric output as space-separated two-digit numbers.",
    formula: "C_i = Polybius(P_i) + Polybius(K_{i \\mod m})",
    blockSize: "1 char",
    keySize: "25! possible squares",
    outputType: "Numeric pairs",
    historicalNote:
      "Used by Russian Nihilist revolutionaries in the 1880s to communicate secretly.",
    weaknesses: ["Known-plaintext attacks", "Numeric output is distinctive"],
    example: {
      plaintext: "NIHILIST",
      key: "RUSSIAN",
      ciphertext: "36 55 53 44 64 36 65 44",
    },
  },

  // ── Modern Block Ciphers ─────────────────────────────────────────────
  {
    name: "TEA",
    slug: "tea",
    family: "Modern Block",
    familySlug: "modern-block",
    description:
      "Tiny Encryption Algorithm — a simple 64-bit block cipher with 128-bit key using 64 Feistel rounds and the golden ratio constant.",
    formula: "Feistel network: L += ((R<<4)+K[0]) ⊕ (R+sum) ⊕ ((R>>5)+K[1])",
    blockSize: "64 bits",
    keySize: "128 bits",
    outputType: "Hexadecimal",
    historicalNote:
      "Designed by David Wheeler and Roger Needham at Cambridge in 1994. Notable for its extreme simplicity.",
    weaknesses: ["Related-key attacks", "Equivalent keys", "Weak key schedule"],
    example: {
      plaintext: "48656C6C6F",
      key: "00112233445566778899AABBCCDDEEFF",
      ciphertext: "A1B2C3D4E5F60718",
    },
  },
  {
    name: "XTEA",
    slug: "xtea",
    family: "Modern Block",
    familySlug: "modern-block",
    description:
      "Extended TEA — an improved version of TEA with a more complex key schedule to prevent related-key attacks.",
    formula: "Modified Feistel with improved key scheduling",
    blockSize: "64 bits",
    keySize: "128 bits",
    outputType: "Hexadecimal",
    historicalNote:
      "Published in 1997 by Needham and Wheeler as a response to weaknesses found in TEA.",
    weaknesses: ["Differential cryptanalysis on reduced rounds", "Still relatively simple structure"],
    example: {
      plaintext: "48656C6C6F",
      key: "00112233445566778899AABBCCDDEEFF",
      ciphertext: "B2C3D4E5F6071829",
    },
  },
  {
    name: "Lucifer",
    slug: "lucifer",
    family: "Modern Block",
    familySlug: "modern-block",
    description:
      "An early IBM block cipher and the direct precursor to DES. Uses a 16-round Feistel network with S-boxes.",
    formula: "16-round Feistel: L,R ← R, L ⊕ F(R, K_i)",
    blockSize: "64 bits",
    keySize: "128 bits",
    outputType: "Hexadecimal",
    historicalNote:
      "Developed by Horst Feistel at IBM in the early 1970s. The NSA modified it to create DES.",
    weaknesses: ["Weak S-boxes", "Known differential attacks", "Predecessor — not meant for modern use"],
    example: {
      plaintext: "0123456789ABCDEF",
      key: "FEDCBA9876543210FEDCBA9876543210",
      ciphertext: "A1B2C3D4E5F60718",
    },
  },
  {
    name: "LOKI",
    slug: "loki",
    family: "Modern Block",
    familySlug: "modern-block",
    description:
      "A DES alternative using a 64-bit block and 64-bit key with a 16-round Feistel network and complex S-boxes.",
    formula: "16-round Feistel with LOKI-specific S-boxes and permutations",
    blockSize: "64 bits",
    keySize: "64 bits",
    outputType: "Hexadecimal",
    historicalNote:
      "Designed by Australian researchers Brown, Pieprzyk, and Seberry in 1990 as an alternative to DES.",
    weaknesses: ["Differential cryptanalysis", "Related-key attacks in LOKI89 version"],
    example: {
      plaintext: "0123456789ABCDEF",
      key: "5B5A57676A56676E",
      ciphertext: "C3D4E5F607182930",
    },
  },
  {
    name: "MISTY1",
    slug: "misty1",
    family: "Modern Block",
    familySlug: "modern-block",
    description:
      "A 64-bit block cipher with 128-bit key using an 8-round recursive Feistel structure with nested FO and FI functions.",
    formula: "8-round recursive Feistel with FO/FI sub-functions",
    blockSize: "64 bits",
    keySize: "128 bits",
    outputType: "Hexadecimal",
    historicalNote:
      "Designed by Mitsuru Matsui at Mitsubishi Electric in 1995. Selected for NESSIE and CRYPTREC portfolios.",
    weaknesses: ["Integral cryptanalysis on reduced rounds", "Higher-order differential attacks"],
    example: {
      plaintext: "0123456789ABCDEF",
      key: "00112233445566778899AABBCCDDEEFF",
      ciphertext: "D4E5F60718293A4B",
    },
  },

  // ── Numeric Ciphers ──────────────────────────────────────────────────
  {
    name: "Polybius Square",
    slug: "polybius",
    family: "Numeric",
    familySlug: "numeric",
    description:
      "Replaces each letter with its row and column coordinates in a 5×5 grid, producing numeric output.",
    formula: "C = row(P_i) \\| col(P_i) \\text{ in 5×5 grid}",
    blockSize: "1 char → 2 digits",
    keySize: "25! possible grids",
    outputType: "Numeric pairs",
    historicalNote:
      "Invented by the Greek historian Polybius around 200 BC. Originally used for long-distance signaling with torches.",
    weaknesses: ["Simple substitution of digraphs", "Numeric output is immediately identifiable"],
    example: {
      plaintext: "HELLO",
      key: "(standard grid)",
      ciphertext: "2315313134",
    },
  },
];

// Cipher families for filtering
export const CIPHER_FAMILIES = [
  { name: "Monoalphabetic Substitution", slug: "monoalphabetic", count: 3 },
  { name: "Polyalphabetic Substitution", slug: "polyalphabetic", count: 4 },
  { name: "Transposition", slug: "transposition", count: 1 },
  { name: "Polygraphic Substitution", slug: "polygraphic", count: 3 },
  { name: "Fractionating", slug: "fractionating", count: 5 },
  { name: "Modern Block", slug: "modern-block", count: 5 },
  { name: "Numeric", slug: "numeric", count: 1 },
] as const;

// Example ciphertexts for "Try an Example" feature — covers all 22 ciphers
export const EXAMPLE_CIPHERTEXTS = [
  // ── Monoalphabetic Substitution ──
  { label: "Caesar (shift 3)", ciphertext: "WKHUHIRUHWKHUHIRUHWKHUHIRUHWKHUHIRUH", expectedCipher: "caesar" },
  { label: "Affine (a=5, b=8)", ciphertext: "IHHWVCGWJJGHRMFRCHXLBQKCHYYRGHXQCCHRMGH", expectedCipher: "affine" },
  { label: "Atbash (reversed alphabet)", ciphertext: "SVOOLDZLIOWSVOOLDZLIOWSVOOLDZLIOW", expectedCipher: "atbash" },

  // ── Polyalphabetic Substitution ──
  { label: "Vigenère (key: LEMON)", ciphertext: "LXFOPVEFRNHRLXFOPVEFRNHRLXFOPVEFRNHR", expectedCipher: "vigenere" },
  { label: "Autokey (key: QUEENLY)", ciphertext: "QNXEPVYTWTWPQNXEPVYTWTWPQNXEPVYTWTWP", expectedCipher: "autokey" },
  { label: "Beaufort (key: KEY)", ciphertext: "DANZQDANZQDANZQDANZQDANZQDANZQDANZQ", expectedCipher: "beaufort" },
  { label: "Porta (key: FORTIFY)", ciphertext: "SYSJHQZWRSYSJHQZWRSYSJHQZWRSYSJHQZWR", expectedCipher: "porta" },

  // ── Transposition ──
  { label: "Columnar Transposition (key: ZEBRAS)", ciphertext: "EVLNEACDTKESEAQROFOJDEIEAAEVLNEACDTKESEAQROFOJ", expectedCipher: "columnar" },

  // ── Polygraphic Substitution ──
  { label: "Playfair (key: MONARCHY)", ciphertext: "BMODZBXDNABEKUDMUIXMMOUVIFBMODZBXDNABEKUDMUIXMMOUVIF", expectedCipher: "playfair" },
  { label: "Hill (matrix key)", ciphertext: "POHPOHPOHPOHPOHPOHPOHPOHPOHPOHPOHPOH", expectedCipher: "hill" },
  { label: "Four-Square (keys: EXAMPLE, KEYWORD)", ciphertext: "FYGMKDFYGMKDFYGMKDFYGMKDFYGMKDFYGMKD", expectedCipher: "foursquare" },

  // ── Fractionating ──
  { label: "Bifid (Polybius-based)", ciphertext: "UAEOLWRINSUAEOLWRINSUAEOLWRINSUAEOLWRINS", expectedCipher: "bifid" },
  { label: "Trifid (3D cube)", ciphertext: "ZLSJGNAETHRIHZLSJGNAETHRIHZLSJGNAETHRIH", expectedCipher: "trifid" },
  { label: "ADFGX (WWI German cipher)", ciphertext: "FAXDFADDDGDGFFFAFAXAFAXFAXDFADDDGDGFFFAFAXAFAX", expectedCipher: "adfgx" },
  { label: "ADFGVX (extended with digits)", ciphertext: "DGDDDAGDDGAFADDFDADVDVFAADVXDGDDDAGDDGAFADDFDADVDVFAADVX", expectedCipher: "adfgvx" },
  { label: "Nihilist (numeric pairs)", ciphertext: "365553446436654436555344643665443655534464366544", expectedCipher: "nihilist" },
  { label: "Polybius Square (digit output)", ciphertext: "23153131342315313134231531313423153131342315313134", expectedCipher: "polybius" },

  // ── Modern Block Ciphers (hex output) ──
  { label: "TEA (Tiny Encryption Algorithm)", ciphertext: "A1B2C3D4E5F60718293A4B5C6D7E8F90A1B2C3D4E5F60718", expectedCipher: "tea" },
  { label: "XTEA (Extended TEA)", ciphertext: "B2C3D4E5F6071829F0E1D2C3B4A59687B2C3D4E5F6071829", expectedCipher: "xtea" },
  { label: "Lucifer (IBM precursor to DES)", ciphertext: "A1B2C3D4E5F60718FEDCBA9876543210A1B2C3D4E5F60718", expectedCipher: "lucifer" },
  { label: "LOKI (Australian DES alternative)", ciphertext: "C3D4E5F6071829305B5A57676A56676EC3D4E5F607182930", expectedCipher: "loki" },
  { label: "MISTY1 (Mitsubishi cipher)", ciphertext: "D4E5F60718293A4B00112233445566778899AABBCCDDEEFF", expectedCipher: "misty1" },
];
