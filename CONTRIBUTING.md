# Contributing to CipherLens

Thanks for your interest in contributing. CipherLens is a research project and we welcome improvements across the board — new ciphers, better models, UI enhancements, and bug fixes.

## Ways to Contribute

### Add a new cipher
The most impactful contribution. To add a cipher:

1. **Implement the cipher** in `backend/scripts/generate_dataset_v4.py`
   - Add an encryption function following the existing pattern
   - Add the cipher to the `CIPHER_FAMILIES` dict
   - Assign it a family or propose a new one

2. **Add cipher metadata** to `frontend/src/lib/constants.ts`
   - Name, family, description, example ciphertext, formula, key info

3. **Retrain the models** — new classes require retraining all three models from scratch (see [Training](README.md#training))

4. Open a PR with the cipher implementation + constants update. Model retraining is handled by maintainers.

**Good candidates for new ciphers:**
- Rail Fence (transposition family)
- Double Columnar Transposition
- Beaufort Variant / Running Key
- Gronsfeld
- ADFGX variant ciphers

---

### Improve model accuracy

Current weak spots (see `docs/FINDINGS.md`):
- Vigenere is never predicted #1 — confused with Hill
- Playfair ↔ Four-Square persistent swap
- Modern block ciphers (TEA/XTEA/Lucifer/LOKI/MISTY1) near-indistinguishable
- Trifid poorly identified

Ideas:
- New statistical features that better separate these pairs
- Ensemble: meta-classifier on top of all 3 model outputs
- Transformer-based architecture for better long-range pattern detection
- Per-period features for Kasiski analysis improvements

---

### Frontend / UI improvements

- Improve mobile layout
- Add copy-to-clipboard for cipher examples
- Dark/light mode persistence
- Accessibility improvements (keyboard navigation, ARIA labels)
- Better empty states and loading skeletons

---

### Bug fixes and general improvements

Check the [issues tab](https://github.com/LordAizen1/cipherlens/issues) for open bugs and feature requests.

---

## Getting Started

```bash
git clone https://github.com/LordAizen1/cipherlens.git
cd cipherlens

# Frontend
cd frontend && npm install && npm run dev

# Backend (separate terminal)
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## PR Guidelines

- **One thing per PR** — don't bundle unrelated changes
- **Test your changes** — run `npm run build` (frontend) and check the backend starts without errors
- **Describe what and why** — a short summary in the PR description is enough
- For new ciphers, include a sample ciphertext in the PR description so we can verify it works

---

## Questions?

Open a [GitHub Discussion](https://github.com/LordAizen1/cipherlens/discussions) or an issue. We're happy to help you get started.
