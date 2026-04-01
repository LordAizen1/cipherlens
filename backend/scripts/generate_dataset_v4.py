#!/usr/bin/env python3
"""
generate_dataset_v4.py — CipherLens dataset generator V4

Usage:
  python generate_dataset_v4.py [--samples N] [--out PATH] [--seed SEED]

Generates N samples per cipher (default: 25000) across all 22 ciphers.
Output: CSV with 19 columns (cipher, family, plaintext, ciphertext, 15 features)

V4 improvements over V3:
  1. 200-500 char plaintexts  (V3 used 64-200)
  2. 25k samples per cipher   (V3 had ~15k)
  3. English letter-frequency distribution for plaintexts
  4. Wider key diversity across all ciphers
  5. New feature: max_kasiski_ioc — best-period average IoC (periods 2-20)
     Helps discriminate polyalphabetic from polygraphic/fractionating ciphers.
"""

import os
import math
import zlib
import struct
import random
import string
import argparse
import numpy as np
import pandas as pd
from collections import Counter
from tqdm import tqdm

# ──────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────
SAMPLES_PER_CIPHER = 25_000
MIN_LEN = 200
MAX_LEN = 500
SEED = 42

CIPHERS = [
    ("caesar",   "mono"),
    ("affine",   "mono"),
    ("atbash",   "mono"),
    ("vigenere", "poly"),
    ("autokey",  "poly"),
    ("beaufort", "poly"),
    ("porta",    "poly"),
    ("columnar", "transposition"),
    ("playfair", "polygraphic"),
    ("hill",     "polygraphic"),
    ("foursquare", "polygraphic"),
    ("bifid",    "fractionating"),
    ("trifid",   "fractionating"),
    ("adfgx",    "fractionating"),
    ("adfgvx",   "fractionating"),
    ("nihilist", "fractionating"),
    ("polybius", "fractionating"),
    ("tea",      "modern"),
    ("xtea",     "modern"),
    ("lucifer",  "modern"),
    ("loki",     "modern"),
    ("misty1",   "modern"),
]

# English letter frequencies (A-Z weights)
_ENG_LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_ENG_WEIGHTS  = [8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15,
                 0.8, 4.0, 2.4, 6.7,  7.5, 1.9, 0.1, 6.0, 6.3,  9.1,
                 2.8, 1.0, 2.4, 0.15, 2.0, 0.07]


# ──────────────────────────────────────────────────────────────
# Plaintext generation
# ──────────────────────────────────────────────────────────────
def random_plaintext(rng: random.Random, min_len=MIN_LEN, max_len=MAX_LEN) -> str:
    length = rng.randint(min_len, max_len)
    return "".join(rng.choices(_ENG_LETTERS, weights=_ENG_WEIGHTS, k=length))


def alpha_key(rng: random.Random, min_len=4, max_len=12) -> str:
    length = rng.randint(min_len, max_len)
    return "".join(rng.choices(string.ascii_uppercase, k=length))


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def make_polybius_square(keyword: str):
    """Return a 25-char string (I=J omitted) ordered by keyword."""
    kw = keyword.upper().replace("J", "I")
    seen = []
    for ch in kw + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if ch not in seen:
            seen.append(ch)
    return "".join(seen)


def polybius_coords(sq: str, ch: str):
    ch = ch.upper().replace("J", "I")
    idx = sq.index(ch)
    return idx // 5, idx % 5


def polybius_from_coords(sq: str, r: int, c: int) -> str:
    return sq[r * 5 + c]


# ──────────────────────────────────────────────────────────────
# MONOALPHABETIC
# ──────────────────────────────────────────────────────────────
def encrypt_caesar(pt: str, rng: random.Random) -> str:
    shift = rng.randint(1, 25)
    return "".join(chr((ord(c) - 65 + shift) % 26 + 65) for c in pt)


_AFFINE_A = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]  # gcd(a,26)=1

def encrypt_affine(pt: str, rng: random.Random) -> str:
    a = rng.choice(_AFFINE_A)
    b = rng.randint(0, 25)
    return "".join(chr((a * (ord(c) - 65) + b) % 26 + 65) for c in pt)


def encrypt_atbash(pt: str, _rng) -> str:
    return "".join(chr(90 - (ord(c) - 65)) for c in pt)


# ──────────────────────────────────────────────────────────────
# POLYALPHABETIC
# ──────────────────────────────────────────────────────────────
def encrypt_vigenere(pt: str, rng: random.Random) -> str:
    key = alpha_key(rng, 3, 16)
    m = len(key)
    return "".join(
        chr((ord(c) - 65 + ord(key[i % m]) - 65) % 26 + 65)
        for i, c in enumerate(pt)
    )


def encrypt_autokey(pt: str, rng: random.Random) -> str:
    kw = alpha_key(rng, 4, 10)
    running = kw + pt
    ct = []
    for i, c in enumerate(pt):
        shift = ord(running[i]) - 65
        ct.append(chr((ord(c) - 65 + shift) % 26 + 65))
    return "".join(ct)


def encrypt_beaufort(pt: str, rng: random.Random) -> str:
    key = alpha_key(rng, 3, 16)
    m = len(key)
    return "".join(
        chr((ord(key[i % m]) - 65 - (ord(c) - 65)) % 26 + 65)
        for i, c in enumerate(pt)
    )


# Porta tableau — 13 rows, each is the 13-char substitution for second-half of alphabet
_PORTA_TABLE = [
    "NOPQRSTUVWXYZ",  # A/B
    "NOPQRSTUVWXZY",  # C/D
    "NOPQRSTUVWYZX",  # E/F
    "NOPQRSTUVXYZW",  # G/H
    "NOPQRSTUWXYZV",  # I/J
    "NOPQRSTUVWXYZ"[::-1][:13],  # K/L  (reversed for variety)
    "NOPQRSUTVWXYZ",  # M/N
    "NOPQRTSUTVWXY",  # O/P  -- small variant
    "NOPQSRTUVWXYZ",  # Q/R
    "NOPRQSTUVWXYZ",  # S/T
    "NOQPRSTUVWXYZ",  # U/V
    "NPOQURSTUVWXY",  # W/X
    "OPQRSTUVWXYZA",  # Y/Z  -- wraps
]

def encrypt_porta(pt: str, rng: random.Random) -> str:
    key = alpha_key(rng, 4, 12)
    m = len(key)
    ct = []
    for i, c in enumerate(pt):
        ki = (ord(key[i % m]) - 65) // 2  # 0-12
        pi = ord(c) - 65                   # 0-25
        row = _PORTA_TABLE[ki % 13]
        if pi < 13:
            # first half (A-M): output second half via tableau
            ct.append(row[pi])
        else:
            # second half (N-Z): find position in row, output that letter A-M
            ch_n = chr(pi + 65)
            if ch_n in row:
                ct.append(chr(row.index(ch_n) + 65))
            else:
                ct.append(c)
    return "".join(ct)


# ──────────────────────────────────────────────────────────────
# TRANSPOSITION
# ──────────────────────────────────────────────────────────────
def encrypt_columnar(pt: str, rng: random.Random) -> str:
    num_cols = rng.randint(3, 12)
    # Pad to fill grid
    pad_len = (num_cols - len(pt) % num_cols) % num_cols
    padded = pt + "X" * pad_len
    num_rows = len(padded) // num_cols
    # Random column order
    order = list(range(num_cols))
    rng.shuffle(order)
    # Read column by column in shuffled order
    grid = [list(padded[r * num_cols:(r + 1) * num_cols]) for r in range(num_rows)]
    return "".join("".join(grid[r][c] for r in range(num_rows)) for c in order)


# ──────────────────────────────────────────────────────────────
# POLYGRAPHIC
# ──────────────────────────────────────────────────────────────
def _playfair_grid(keyword: str):
    return make_polybius_square(keyword)

def encrypt_playfair(pt: str, rng: random.Random) -> str:
    keyword = alpha_key(rng, 4, 10)
    sq = _playfair_grid(keyword)
    # Prepare bigrams: replace J->I, insert X between double letters, pad if odd
    cleaned = pt.upper().replace("J", "I")
    bigrams = []
    i = 0
    while i < len(cleaned):
        a = cleaned[i]
        if i + 1 < len(cleaned):
            b = cleaned[i + 1]
            if a == b:
                bigrams.append((a, "X"))
                i += 1
            else:
                bigrams.append((a, b))
                i += 2
        else:
            bigrams.append((a, "X"))
            i += 1

    ct = []
    for a, b in bigrams:
        if a not in sq or b not in sq:
            ct.extend([a, b])
            continue
        r1, c1 = polybius_coords(sq, a)
        r2, c2 = polybius_coords(sq, b)
        if r1 == r2:
            ct.append(polybius_from_coords(sq, r1, (c1 + 1) % 5))
            ct.append(polybius_from_coords(sq, r2, (c2 + 1) % 5))
        elif c1 == c2:
            ct.append(polybius_from_coords(sq, (r1 + 1) % 5, c1))
            ct.append(polybius_from_coords(sq, (r2 + 1) % 5, c2))
        else:
            ct.append(polybius_from_coords(sq, r1, c2))
            ct.append(polybius_from_coords(sq, r2, c1))
    return "".join(ct)


def _valid_hill_2x2(rng: random.Random):
    """Return a random invertible 2x2 matrix mod 26."""
    for _ in range(1000):
        a, b = rng.randint(0, 25), rng.randint(0, 25)
        c, d = rng.randint(0, 25), rng.randint(0, 25)
        det = (a * d - b * c) % 26
        if math.gcd(det, 26) == 1:
            return [[a, b], [c, d]]
    return [[1, 2], [3, 5]]  # fallback (det=5-6=-1≡25, gcd(25,26)=1 ✓ ... actually det=5*1-2*3=-1≡25)


def encrypt_hill(pt: str, rng: random.Random) -> str:
    mat = _valid_hill_2x2(rng)
    # Pad to even length
    if len(pt) % 2:
        pt += "X"
    ct = []
    for i in range(0, len(pt), 2):
        x = ord(pt[i]) - 65
        y = ord(pt[i + 1]) - 65
        ct.append(chr((mat[0][0] * x + mat[0][1] * y) % 26 + 65))
        ct.append(chr((mat[1][0] * x + mat[1][1] * y) % 26 + 65))
    return "".join(ct)


def encrypt_foursquare(pt: str, rng: random.Random) -> str:
    kw1 = alpha_key(rng, 5, 9)
    kw2 = alpha_key(rng, 5, 9)
    sq_std = make_polybius_square("")   # ABCDE...Z (no J)
    sq1   = make_polybius_square(kw1)
    sq2   = make_polybius_square(kw2)
    # Pad to even
    cleaned = pt.replace("J", "I")
    if len(cleaned) % 2:
        cleaned += "X"
    ct = []
    for i in range(0, len(cleaned), 2):
        a, b = cleaned[i], cleaned[i + 1]
        r1, c1 = polybius_coords(sq_std, a)
        r2, c2 = polybius_coords(sq_std, b)
        ct.append(polybius_from_coords(sq1, r1, c2))
        ct.append(polybius_from_coords(sq2, r2, c1))
    return "".join(ct)


# ──────────────────────────────────────────────────────────────
# FRACTIONATING
# ──────────────────────────────────────────────────────────────
def encrypt_bifid(pt: str, rng: random.Random) -> str:
    period = rng.randint(5, 10)
    keyword = alpha_key(rng, 4, 8)
    sq = make_polybius_square(keyword)
    cleaned = pt.replace("J", "I")

    ct = []
    for chunk_start in range(0, len(cleaned), period):
        chunk = cleaned[chunk_start:chunk_start + period]
        rows, cols = [], []
        for ch in chunk:
            r, c = polybius_coords(sq, ch)
            rows.append(r)
            cols.append(c)
        combined = rows + cols
        for i in range(0, len(combined) - 1, 2):
            ct.append(polybius_from_coords(sq, combined[i], combined[i + 1]))
    return "".join(ct)


# 3x3x3 Trifid cube — 27 letters (use A-Z + '#' for the 27th slot, or skip)
_TRIFID_ALPHA = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ+")  # 27 chars

def encrypt_trifid(pt: str, rng: random.Random) -> str:
    period = rng.randint(3, 7)
    # Shuffle the 27-char cube
    cube = _TRIFID_ALPHA[:]
    rng.shuffle(cube)
    char_to_idx = {ch: i for i, ch in enumerate(cube)}
    cleaned = pt.replace("J", "I")

    ct = []
    for chunk_start in range(0, len(cleaned), period):
        chunk = cleaned[chunk_start:chunk_start + period]
        l_vals, r_vals, c_vals = [], [], []
        for ch in chunk:
            if ch not in char_to_idx:
                ch = "A"
            idx = char_to_idx[ch]
            l_vals.append(idx // 9)
            r_vals.append((idx % 9) // 3)
            c_vals.append(idx % 3)
        combined = l_vals + r_vals + c_vals
        for i in range(0, len(combined) - 2, 3):
            tri_idx = combined[i] * 9 + combined[i + 1] * 3 + combined[i + 2]
            out_char = cube[tri_idx % 27]
            if out_char == "+":
                out_char = "X"
            ct.append(out_char)
    return "".join(ct)


_ADFGX_LABELS = "ADFGX"

def encrypt_adfgx(pt: str, rng: random.Random) -> str:
    alpha = list("ABCDEFGHIKLMNOPQRSTUVWXYZ")  # 25 (no J)
    rng.shuffle(alpha)
    char_to_coord = {
        ch: (_ADFGX_LABELS[i // 5], _ADFGX_LABELS[i % 5])
        for i, ch in enumerate(alpha)
    }
    # Step 1: fractionation
    frac = []
    for ch in pt:
        ch = ch.replace("J", "I")
        if ch in char_to_coord:
            frac.extend(char_to_coord[ch])
        else:
            frac.extend((_ADFGX_LABELS[0], _ADFGX_LABELS[0]))
    # Step 2: columnar transposition
    num_cols = rng.randint(3, 8)
    pad = (num_cols - len(frac) % num_cols) % num_cols
    frac.extend(["A"] * pad)
    num_rows = len(frac) // num_cols
    order = list(range(num_cols))
    rng.shuffle(order)
    grid = [frac[r * num_cols:(r + 1) * num_cols] for r in range(num_rows)]
    return "".join("".join(grid[r][c] for r in range(num_rows)) for c in order)


_ADFGVX_LABELS = "ADFGVX"
_ADFGVX_CHARS  = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

def encrypt_adfgvx(pt: str, rng: random.Random) -> str:
    chars = _ADFGVX_CHARS[:]
    rng.shuffle(chars)
    char_to_coord = {
        ch: (_ADFGVX_LABELS[i // 6], _ADFGVX_LABELS[i % 6])
        for i, ch in enumerate(chars)
    }
    frac = []
    for ch in pt:
        if ch in char_to_coord:
            frac.extend(char_to_coord[ch])
        else:
            frac.extend(("A", "A"))
    num_cols = rng.randint(3, 8)
    pad = (num_cols - len(frac) % num_cols) % num_cols
    frac.extend(["A"] * pad)
    num_rows = len(frac) // num_cols
    order = list(range(num_cols))
    rng.shuffle(order)
    grid = [frac[r * num_cols:(r + 1) * num_cols] for r in range(num_rows)]
    return "".join("".join(grid[r][c] for r in range(num_rows)) for c in order)


def encrypt_nihilist(pt: str, rng: random.Random) -> str:
    sq_kw = alpha_key(rng, 3, 8)
    key_kw = alpha_key(rng, 3, 8)
    sq = make_polybius_square(sq_kw)
    # Polybius coords for key
    num_key = []
    for ch in key_kw:
        ch = ch.replace("J", "I")
        r, c = polybius_coords(sq, ch)
        num_key.append((r + 1) * 10 + (c + 1))
    # Encrypt plaintext
    nums = []
    for i, ch in enumerate(pt):
        ch = ch.replace("J", "I")
        r, c = polybius_coords(sq, ch)
        pt_num = (r + 1) * 10 + (c + 1)
        nums.append(str(pt_num + num_key[i % len(num_key)]))
    return " ".join(nums)


def encrypt_polybius(pt: str, rng: random.Random) -> str:
    keyword = alpha_key(rng, 3, 8)
    sq = make_polybius_square(keyword)
    nums = []
    for ch in pt:
        ch = ch.replace("J", "I")
        r, c = polybius_coords(sq, ch)
        nums.append(f"{r + 1}{c + 1}")
    return " ".join(nums)


# ──────────────────────────────────────────────────────────────
# MODERN BLOCK CIPHERS — output hex strings
# ──────────────────────────────────────────────────────────────

def _pt_to_bytes(pt: str) -> bytes:
    """Encode plaintext to bytes for block cipher input."""
    return pt.encode("ascii", errors="replace")


def _random_key_bytes(rng: random.Random, n: int) -> bytes:
    return bytes(rng.randint(0, 255) for _ in range(n))


# ── TEA ──────────────────────────────────────────────────────
def _tea_encrypt_block(v0: int, v1: int, key) -> tuple:
    k0, k1, k2, k3 = key
    delta = 0x9E3779B9
    s = 0
    for _ in range(32):
        s = (s + delta) & 0xFFFFFFFF
        v0 = (v0 + (((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1))) & 0xFFFFFFFF
        v1 = (v1 + (((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3))) & 0xFFFFFFFF
    return v0, v1


def encrypt_tea(pt: str, rng: random.Random) -> str:
    key_bytes = _random_key_bytes(rng, 16)
    k = struct.unpack(">4I", key_bytes)
    data = _pt_to_bytes(pt)
    result = bytearray()
    for i in range(0, len(data), 8):
        block = data[i:i + 8].ljust(8, b"\x00")
        v0, v1 = struct.unpack(">2I", block)
        v0, v1 = _tea_encrypt_block(v0, v1, k)
        result += struct.pack(">2I", v0, v1)
    return result.hex()


# ── XTEA ─────────────────────────────────────────────────────
def _xtea_encrypt_block(v0: int, v1: int, key) -> tuple:
    delta = 0x9E3779B9
    s = 0
    for _ in range(32):
        v0 = (v0 + (((v1 << 4 ^ v1 >> 5) + v1) ^ (s + key[s & 3]))) & 0xFFFFFFFF
        s = (s + delta) & 0xFFFFFFFF
        v1 = (v1 + (((v0 << 4 ^ v0 >> 5) + v0) ^ (s + key[(s >> 11) & 3]))) & 0xFFFFFFFF
    return v0, v1


def encrypt_xtea(pt: str, rng: random.Random) -> str:
    key_bytes = _random_key_bytes(rng, 16)
    k = struct.unpack(">4I", key_bytes)
    data = _pt_to_bytes(pt)
    result = bytearray()
    for i in range(0, len(data), 8):
        block = data[i:i + 8].ljust(8, b"\x00")
        v0, v1 = struct.unpack(">2I", block)
        v0, v1 = _xtea_encrypt_block(v0, v1, k)
        result += struct.pack(">2I", v0, v1)
    return result.hex()


# ── Lucifer (IBM 1973 Feistel, 64-bit block, 128-bit key, 16 rounds) ──
_LUCIFER_S0 = [12, 15,  7, 10, 14, 13, 11,  0,  2,  6,  3,  1,  9,  4,  5,  8]
_LUCIFER_S1 = [ 7,  2, 14,  9,  3, 11,  0,  4, 12, 13,  1, 10,  6, 15,  8,  5]

def _lucifer_f(half: int, subkey: int) -> int:
    """Lucifer round function: S-boxes + key mixing on 32-bit half."""
    x = half ^ subkey
    out = 0
    for i in range(8):
        nibble = (x >> (i * 4)) & 0xF
        s = _LUCIFER_S0[nibble] if (i % 2 == 0) else _LUCIFER_S1[nibble]
        out |= (s << (i * 4))
    # Simple diffusion: rotate left 13
    out = ((out << 13) | (out >> 19)) & 0xFFFFFFFF
    return out


def encrypt_lucifer(pt: str, rng: random.Random) -> str:
    key_bytes = _random_key_bytes(rng, 16)
    # Derive 16 round subkeys (32-bit each) from 128-bit key
    subkeys = list(struct.unpack(">4I", key_bytes))
    # Expand to 16 subkeys by rotating
    full_keys = []
    for i in range(16):
        idx = i % 4
        rot = (i // 4) * 3
        sk = subkeys[idx]
        sk = ((sk << rot) | (sk >> (32 - rot))) & 0xFFFFFFFF if rot else sk
        full_keys.append(sk ^ subkeys[(idx + 1) % 4])

    data = _pt_to_bytes(pt)
    result = bytearray()
    for i in range(0, len(data), 8):
        block = data[i:i + 8].ljust(8, b"\x00")
        L, R = struct.unpack(">2I", block)
        for rnd in range(16):
            L, R = R, L ^ _lucifer_f(R, full_keys[rnd])
        result += struct.pack(">2I", L, R)
    return result.hex()


# ── LOKI91 (simplified Feistel, 64-bit block, 64-bit key, 16 rounds) ──
# S-box built from a primitive polynomial GF(2^12) construction (simplified)
def _loki91_sbox():
    """Build LOKI91-style 12→8 bit S-box."""
    box = []
    for x in range(256):
        # Simplified LOKI91 S-box: use polynomial GF(2^8) squaring + affine map
        val = x
        # Mix nibbles
        hi = (val >> 4) & 0xF
        lo = val & 0xF
        mix = ((hi * 13 + lo * 7 + 5) ^ (lo * hi + 3)) & 0xFF
        box.append(mix)
    return box

_LOKI_SBOX = _loki91_sbox()

def _loki91_f(half: int, subkey: int) -> int:
    x = (half + subkey) & 0xFFFFFFFF
    out = 0
    for i in range(4):
        byte = (x >> (i * 8)) & 0xFF
        out |= (_LOKI_SBOX[byte] << (i * 8))
    # P-permutation: rotate left 11
    out = ((out << 11) | (out >> 21)) & 0xFFFFFFFF
    return out


def encrypt_loki(pt: str, rng: random.Random) -> str:
    key_bytes = _random_key_bytes(rng, 8)
    KL, KR = struct.unpack(">2I", key_bytes)
    # Key schedule: 16 subkeys via alternating XOR + rotate
    subkeys = []
    kl, kr = KL, KR
    for i in range(16):
        subkeys.append(kl if i % 2 == 0 else kr)
        kl = ((kl << 3) | (kl >> 29)) & 0xFFFFFFFF ^ kr
        kr = ((kr << 5) | (kr >> 27)) & 0xFFFFFFFF ^ kl

    data = _pt_to_bytes(pt)
    result = bytearray()
    for i in range(0, len(data), 8):
        block = data[i:i + 8].ljust(8, b"\x00")
        L, R = struct.unpack(">2I", block)
        for rnd in range(16):
            L, R = R, L ^ _loki91_f(R, subkeys[rnd])
        result += struct.pack(">2I", L, R)
    return result.hex()


# ── MISTY1 (simplified FL/FO/FI structure, 64-bit block, 128-bit key) ──
def _fi(in16: int, ki9: int, ki7: int) -> int:
    """MISTY1 FI function (simplified 16-bit → 16-bit)."""
    d9 = (in16 >> 7) & 0x1FF
    d7 = in16 & 0x7F
    # S9-like substitution: mix with ki9
    d9 = (d9 ^ ki9) & 0x1FF
    # S7-like substitution
    d7 = (d7 ^ (d9 & 0x7F)) & 0x7F
    d9 = (d9 ^ (d7 >> 1)) & 0x1FF
    d7 = (d7 ^ ki7) & 0x7F
    return (d9 << 7) | d7


def _fo(in32: int, k: list, round_idx: int) -> int:
    """MISTY1 FO function (32-bit → 32-bit)."""
    t0 = (in32 >> 16) & 0xFFFF
    t1 = in32 & 0xFFFF
    t0 = t0 ^ k[round_idx % len(k)]
    t0 = _fi(t0, k[(round_idx + 1) % len(k)] & 0x1FF,
              k[(round_idx + 2) % len(k)] & 0x7F)
    t1 ^= t0
    t1 = _fi(t1, k[(round_idx + 3) % len(k)] & 0x1FF,
              k[(round_idx + 4) % len(k)] & 0x7F)
    t0 ^= t1
    return (t0 << 16) | t1


def _fl(in32: int, kl: int) -> int:
    """MISTY1 FL function (32-bit → 32-bit)."""
    r = (in32 >> 16) & 0xFFFF
    l = in32 & 0xFFFF
    r ^= ((l & kl) >> 1) & 0x7FFF  # simplified
    l ^= r | ((kl >> 16) & 0xFFFF)
    return (r << 16) | l


def encrypt_misty1(pt: str, rng: random.Random) -> str:
    key_bytes = _random_key_bytes(rng, 16)
    # Expand key to 8 subkeys (16-bit each)
    ks = list(struct.unpack(">8H", key_bytes))

    data = _pt_to_bytes(pt)
    result = bytearray()
    for i in range(0, len(data), 8):
        block = data[i:i + 8].ljust(8, b"\x00")
        D0, D1 = struct.unpack(">2I", block)
        for rnd in range(8):
            D0 = _fl(D0, (ks[rnd % 8] << 16) | ks[(rnd + 1) % 8])
            D1 = _fl(D1, (ks[(rnd + 2) % 8] << 16) | ks[(rnd + 3) % 8])
            D0 ^= _fo(D1, ks, rnd)
            D0, D1 = D1, D0
        result += struct.pack(">2I", D0, D1)
    return result.hex()


# ──────────────────────────────────────────────────────────────
# FEATURE EXTRACTION (15 features = 14 existing + max_kasiski_ioc)
# ──────────────────────────────────────────────────────────────
def extract_features(cipher_str: str) -> list:
    text = str(cipher_str)
    data = text.encode("utf-8", errors="ignore")
    total = len(data)
    if total == 0:
        return [0.0] * 15

    freqs = Counter(data)
    entropy = -sum((f / total) * math.log2(f / total) for f in freqs.values())
    compression = len(zlib.compress(data)) / total

    if total > 1:
        bigrams = [data[i:i + 2] for i in range(total - 1)]
        f2 = Counter(bigrams)
        t2 = len(bigrams)
        bigram_entropy = -sum((f / t2) * math.log2(f / t2) for f in f2.values())
    else:
        bigram_entropy = 0.0

    if total > 2:
        trigrams = [data[i:i + 3] for i in range(total - 2)]
        f3 = Counter(trigrams)
        t3 = len(trigrams)
        trigram_entropy = -sum((f / t3) * math.log2(f / t3) for f in f3.values())
    else:
        trigram_entropy = 0.0

    vals = list(freqs.values())
    uniformity = float(np.std(vals)) if vals else 0.0
    unique_ratio = len(freqs) / total

    transitions = Counter(zip(data, data[1:]))
    transition_var = float(np.var(list(transitions.values()))) if transitions else 0.0

    runs, current = [], 1
    for i in range(1, total):
        if data[i] == data[i - 1]:
            current += 1
        else:
            runs.append(current)
            current = 1
    runs.append(current)
    run_length_mean = float(np.mean(runs))
    run_length_var = float(np.var(runs))

    # IoC on alpha chars, fallback to digits
    alpha_chars = [c for c in text if c.isalpha()]
    if len(alpha_chars) > 1:
        fc = Counter(alpha_chars)
        N = len(alpha_chars)
        ioc = sum(v * (v - 1) for v in fc.values()) / (N * (N - 1))
    else:
        digit_chars = [c for c in text if c.isdigit()]
        if len(digit_chars) > 1:
            fc = Counter(digit_chars)
            N = len(digit_chars)
            ioc = sum(v * (v - 1) for v in fc.values()) / (N * (N - 1))
        else:
            ioc = 0.0

    # IoC variance (periods 2-9, existing feature)
    work_chars = alpha_chars if len(alpha_chars) > 1 else [c for c in text if c.isdigit()]
    work_text = "".join(work_chars)
    if len(work_text) > 2:
        ioc_vars = []
        for period in range(2, 10):
            slices = ["".join(work_text[i::period]) for i in range(period)]
            p_vals = []
            for s in slices:
                if len(s) > 1:
                    fc = Counter(s)
                    N2 = len(s)
                    p_vals.append(sum(v * (v - 1) for v in fc.values()) / (N2 * (N2 - 1)))
            if p_vals:
                ioc_vars.append(np.var(p_vals))
        ioc_variance = float(np.mean(ioc_vars)) if ioc_vars else 0.0
    else:
        ioc_variance = 0.0

    txt_len = max(len(text), 1)
    digit_ratio = sum(1 for c in text if c.isdigit()) / txt_len
    alpha_ratio = sum(1 for c in text if c.isalpha()) / txt_len

    # NEW: max_kasiski_ioc — best-period average IoC across periods 2-20
    # Peaks at key length for polyalphabetic ciphers (~0.065 for English)
    # Stays low (~0.038) for uniform-output ciphers (Hill, fractionating, modern)
    if len(work_text) >= 40:
        best_ioc = 0.0
        for period in range(2, 21):
            slices = ["".join(work_text[i::period]) for i in range(period)]
            p_iocs = []
            for s in slices:
                if len(s) > 1:
                    fc = Counter(s)
                    N2 = len(s)
                    p_iocs.append(sum(v * (v - 1) for v in fc.values()) / (N2 * (N2 - 1)))
            if p_iocs:
                avg_ioc = float(np.mean(p_iocs))
                best_ioc = max(best_ioc, avg_ioc)
        max_kasiski_ioc = best_ioc
    else:
        max_kasiski_ioc = 0.0

    return [
        float(total), entropy, compression, bigram_entropy, trigram_entropy,
        uniformity, unique_ratio, transition_var, run_length_mean,
        run_length_var, ioc, ioc_variance, digit_ratio, alpha_ratio,
        max_kasiski_ioc,
    ]


FEATURE_COLS = [
    "length", "entropy", "compression", "bigram_entropy", "trigram_entropy",
    "uniformity", "unique_ratio", "transition_var", "run_length_mean",
    "run_length_var", "ioc", "ioc_variance", "digit_ratio", "alpha_ratio",
    "max_kasiski_ioc",
]


# ──────────────────────────────────────────────────────────────
# Dispatch table
# ──────────────────────────────────────────────────────────────
ENCRYPT_FN = {
    "caesar":     encrypt_caesar,
    "affine":     encrypt_affine,
    "atbash":     encrypt_atbash,
    "vigenere":   encrypt_vigenere,
    "autokey":    encrypt_autokey,
    "beaufort":   encrypt_beaufort,
    "porta":      encrypt_porta,
    "columnar":   encrypt_columnar,
    "playfair":   encrypt_playfair,
    "hill":       encrypt_hill,
    "foursquare": encrypt_foursquare,
    "bifid":      encrypt_bifid,
    "trifid":     encrypt_trifid,
    "adfgx":      encrypt_adfgx,
    "adfgvx":     encrypt_adfgvx,
    "nihilist":   encrypt_nihilist,
    "polybius":   encrypt_polybius,
    "tea":        encrypt_tea,
    "xtea":       encrypt_xtea,
    "lucifer":    encrypt_lucifer,
    "loki":       encrypt_loki,
    "misty1":     encrypt_misty1,
}


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=SAMPLES_PER_CIPHER,
                        help="Samples per cipher (default: 25000)")
    parser.add_argument("--out", type=str, default="cipher_MASTER_FULL_V4.csv",
                        help="Output CSV path")
    parser.add_argument("--seed", type=int, default=SEED,
                        help="Random seed (default: 42)")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    np.random.seed(args.seed)

    rows = []
    total_ciphers = len(CIPHERS)

    for cipher_idx, (cipher_name, family) in enumerate(CIPHERS):
        fn = ENCRYPT_FN[cipher_name]
        print(f"[{cipher_idx + 1}/{total_ciphers}] Generating {args.samples:,} samples for '{cipher_name}'...")
        errors = 0
        with tqdm(total=args.samples, unit="sample", leave=False) as pbar:
            generated = 0
            while generated < args.samples:
                try:
                    pt = random_plaintext(rng)
                    ct = fn(pt, rng)
                    if not ct or ct == pt:
                        continue
                    feats = extract_features(ct)
                    rows.append([cipher_name, family, pt, ct] + feats)
                    generated += 1
                    pbar.update(1)
                except Exception:
                    errors += 1
                    if errors > 100:
                        print(f"  WARNING: {errors} errors for {cipher_name}, check implementation")
                        break
        print(f"  Done. Errors skipped: {errors}")

    print(f"\nBuilding DataFrame ({len(rows):,} rows)...")
    cols = ["cipher", "family", "plaintext", "ciphertext"] + FEATURE_COLS
    df = pd.DataFrame(rows, columns=cols)

    # Shuffle before saving
    df = df.sample(frac=1, random_state=args.seed).reset_index(drop=True)

    print(f"Class distribution:\n{df['cipher'].value_counts().to_string()}\n")

    print(f"Saving to {args.out}...")
    df.to_csv(args.out, index=False)
    print(f"Done! {len(df):,} rows, {len(df.columns)} columns saved to {args.out}")
    print(f"Compress with: gzip {args.out}")


if __name__ == "__main__":
    main()
