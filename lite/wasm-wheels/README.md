# spaCy WebAssembly wheels for JupyterLite

These wheels let `notebooks/01_spacy_basics.ipynb` run spaCy inside the
browser-only JupyterLite deployment (Pyodide's WASM Python runtime cannot
use the regular PyPI wheels for these packages, since spaCy's core is
Cython/C and BLIS uses hand-written SIMD assembly kernels).

They are built from source with [`pyodide-build`](https://pyodide.org/en/stable/development/building-and-testing-packages.html)
cross-compiled against **Pyodide 0.27.6** (the version bundled by
`jupyterlite-pyodide-kernel==0.6.1`, itself used by the `lite` dependency
group in [`pyproject.toml`](../../pyproject.toml)), Python 3.12 / Emscripten
3.1.58. Not distributed on PyPI, so they are committed here directly
(~5.3 MB total) rather than fetched at build time.

## Packages and versions

| Wheel | Version | Notes |
|---|---|---|
| `murmurhash` | 1.0.15 | matches `requirements.txt` |
| `cymem` | 2.0.13 | matches `requirements.txt` |
| `preshed` | 3.0.13 | matches `requirements.txt` |
| `srsly` | 2.5.3 | matches `requirements.txt`, source-patched (see below) |
| `blis` | 1.3.3 | matches `requirements.txt`, built with `BLIS_ARCH=generic` |
| `thinc` | 8.3.13 | matches `requirements.txt` |
| `spacy` | **3.8.13** | one patch behind the `3.8.14` pin used everywhere else — 3.8.14 was never published with an sdist on PyPI, so it can't be built from source for a new target platform |

## How they were built

```bash
pip install 'pyodide-build[resolve]' 'wheel<0.44'   # wheel>=0.46 breaks auditwheel-emscripten
pyodide xbuildenv install 0.27.6

export USE_LEGACY_PLATFORM=true   # pyodide 0.27.6 expects `pyodide_2024_0` wheel tags,
                                    # not the newer `pyemscripten_2024_0` tags pyodide-build
                                    # emits by default
export BLIS_ARCH=generic          # BLIS auto-detects the *build host* CPU (e.g. cortex-a57)
                                    # and tries to compile its hand-written SIMD asm kernels for
                                    # it, which fails for an emscripten/wasm32 target. "generic"
                                    # is BLIS's portable, non-SIMD reference C implementation —
                                    # correct but slower than native BLIS.

for pkg in murmurhash==1.0.15 cymem==2.0.13 preshed==3.0.13 srsly==2.5.3 \
           blis==1.3.3 thinc==8.3.13 spacy==3.8.13; do
  pyodide build "$pkg" -o ./wheels --exports whole_archive
done
```

`--exports whole_archive` is required: by default `pyodide build` only
exports symbols requested by the Python C-API loader, but srsly's vendored
`ultrajson` C library has a cross-translation-unit call to an `inline`
(non-`static`) helper (`strreverse` in `ultrajsonenc.c`) that native
toolchains silently inline away — Emscripten's limited post-link
optimizations (triggered by debug info) sometimes don't, producing a
"cannot resolve symbol strreverse" fatal error at runtime. If rebuilding
srsly from a from a version where this still reproduces, patch
`srsly/ujson/lib/ultrajson.h`: change `#define INLINE_PREFIX inline` to
`#define INLINE_PREFIX static inline` before building.

## Verifying a rebuild

Sanity-checked end-to-end (not just "it compiles") in a real Pyodide 0.27.6
runtime via Node.js — full tokenization, POS tagging, dependency parsing,
NER, word-vector similarity (exercises BLIS), and `displacy` HTML/SVG
rendering all produced correct output for both `en_core_web_md` and
`fr_core_news_md`.
