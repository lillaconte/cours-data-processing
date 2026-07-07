# Data scraping and (pre)processing

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
<!-- [![Binder](https://static.mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/architexte/cours-data-processing/main) -->
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Launch in JupyterLite](https://raw.githubusercontent.com/jupyterlite/jupyterlite/refs/heads/main/docs/_static/badge.svg)](https://lillaconte.github.io/cours-data-processing/lite/lab/index.html)

A practical introduction to collecting and pre-processing textual data in Python, in the context of digital humanities.


Two notebooks:

- **`notebooks/webscraping.ipynb`** — HTTP, HTML, CSV/JSON/XML, `requests`, `BeautifulSoup`, Gallica API, Genius API, DoTS-DTS scrapping, concurrent scrapping
- **`notebooks/spacy_basics.ipynb`** — tokenization, lemmatization, named entity recognition with spaCy

## Genius API key setup

Create a `.env` file (use the [`.dev.env`](./.dev.env) as template) at the root of the project:

```
GENIUS_CLIENT_ACCESS_TOKEN=your_client_access_token_here
```

This file is ignored by git and must never be committed. See [this guide](https://melaniewalsh.github.io/Intro-Cultural-Analytics/04-Data-Collection/07-Genius-API.html#api-keys) to get your key.

## Installation

### With conda

```bash
conda env create -f environment.yml
conda activate sassari
```


### With uv

```bash
uv sync
```

### With pip + venv

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Launch JupyterLab

```bash
# venv or conda (environment already activated)
jupyter lab

# uv
uv run jupyter lab
```

Then open the desired notebook from the `notebooks/` folder.

## Build the site locally (`build.sh`)

[`build.sh`](build.sh) reproduces the whole [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) pipeline (Jupyter Book + spaCy wasm deps + JupyterLite) so you can check the result before pushing, without retyping the commands from the sections below:

```bash
./build.sh --all              # book + spaCy wasm deps + JupyterLite
./build.sh --only book        # Jupyter Book only
./build.sh --only deps        # stage the spaCy wasm wheels + models only
./build.sh --only lite        # JupyterLite only (notebooks/data/img/src)

./build.sh --all --serve      # ...then serve _build/html on http://localhost:8000
```

`--serve` combines with `--all` or any `--only` mode. Requires `npm install -g jupyter-book` once for the `book` step (see below) — `deps` and `lite` only need `uv` (or `pip`, see [Build and test JupyterLite locally](#build-and-test-jupyterlite-locally)).

The sections below detail what each step does and why, useful for troubleshooting or running things by hand.

## Build Jupyter Book

The book is built with [MyST](https://mystmd.org/) (its CLI is published as the npm package `jupyter-book`, matching the GitHub Actions workflow at [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)):

```bash
npm install -g jupyter-book
```

```bash
# Local preview with hot reload, at http://localhost:3000
jupyter book start

# Static HTML build, output in ./_build/html (what CI does)
jupyter book build --html
```

## Build and test JupyterLite locally

A [JupyterLite](https://jupyterlite.readthedocs.io/) deployment (in-browser JupyterLab, no server) is built and published alongside the Jupyter Book, nested under `/lite/` in the same GitHub Pages site. It reuses the exact steps run by CI ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)) so you can reproduce and check the result before pushing.

### 1. Install the build tools

The `lite` dependency group is not installed by a plain `uv sync` — it must be requested explicitly, on **both** `sync` and `run` (otherwise `uv run` re-syncs the default groups only and the `jupyter lite` subcommand won't be found):

```bash
uv sync --group lite
# or: pip install jupyterlite-core==0.6.4 jupyterlite-pyodide-kernel==0.6.1 jupyter-server>=2.19.0
```

### 2. Stage the content and build

```bash
mkdir -p lite_content
cp -r notebooks lite_content/
cp -r data lite_content/
cp -r img lite_content/
cp -r src lite_content/

uv run --group lite jupyter lite build --contents lite_content --output-dir _build/html/lite
# or, without uv: jupyter lite build --contents lite_content --output-dir _build/html/lite

# lite_content/ and the build cache were only needed to produce _build/html/lite/ above — remove them:
rm -rf lite_content .jupyterlite.doit.db
```

If you get a confusing `FileNotFoundError` with a doubled-up path (e.g. `_build/html/_build/html/lite/...`), a stale build cache from a previous run is the cause: delete `_build/` and `.jupyterlite.doit.db` and rebuild from scratch.

This produces a static site in `_build/html/lite/`, with `notebooks/`, `data/`, `img/` and `src/` preserved as sibling folders inside it (so relative paths like `../data/...` or `../img/...` used in the notebooks resolve the same way as in a normal checkout).

Each notebook that needs extra packages in JupyterLite (`01`, `02`, `03`, `04`) has a short setup cell right after its badge, e.g.:

```python
import sys

if sys.platform == "emscripten":
    import js
    from pyodide.http import pyfetch
    _url = js.location.href.split("/lite/")[0] + "/lite/files/src/install_pyodide.py"
    exec(await (await pyfetch(_url)).string())
else:
    sys.path.insert(0, "../src")
    from install_pyodide import install_spacy

await install_spacy()
```

Under JupyterLite this fetches [`src/install_pyodide.py`](src/install_pyodide.py) over HTTP rather than `sys.path.insert(0, "../src")` + a normal import: JupyterLite's browser-side "Drive" is an API-backed virtual filesystem, and while simple file reads (e.g. `../data/...`) work fine against it, Python's import machinery cannot reliably list/traverse it to discover a sibling module — that fails with `ModuleNotFoundError: No module named 'install_pyodide'` even though the file is really there. Fetching over HTTP sidesteps this (it's the same kind of mechanism `piplite` already uses to fetch wheels, which is why that part always worked). Outside JupyterLite (Jupyter Book/JupyterLab/conda/uv), the `else` branch runs instead — a plain, normal import from the real `src/` folder on disk.

All the actual `piplite.install(...)` logic lives in one shared file, [`src/install_pyodide.py`](src/install_pyodide.py), instead of being duplicated across notebooks — it is **not** a notebook you open or run yourself, just a plain Python module loaded by the notebooks that need it. Each function there is a no-op outside JupyterLite (`sys.platform != "emscripten"`), so these cells are harmless to run in a normal Jupyter Book/JupyterLab/conda/uv session too — nothing needs to be skipped or edited when running notebooks outside Lite.

**Important**: each notebook opened in JupyterLite runs in its own, isolated kernel (a fresh Python interpreter per tab). There is no way to "install once" for the whole site — every notebook that needs extra packages calls its own `install_*()` function, cheaply and safely (it's instant if nothing needs installing).

### 3. Stage the spaCy wasm wheels (needed for `01_spacy_basics.ipynb` only)

spaCy's core (and `blis`/`thinc`) are Cython/C, so the regular PyPI wheels can't run in Pyodide's WASM runtime. [`lite/wasm-wheels/`](lite/wasm-wheels/) has custom-built wasm32 wheels for this (see [`lite/wasm-wheels/README.md`](lite/wasm-wheels/README.md) for how they were built and how to rebuild them). CI serves them same-origin because GitHub Releases (where the spaCy language models are hosted) does not send CORS headers, which a browser requires for cross-origin `fetch()`:

```bash
mkdir -p _build/html/lite/extra-wheels
cp lite/wasm-wheels/*.whl _build/html/lite/extra-wheels/
curl -sL -o _build/html/lite/extra-wheels/en_core_web_md-3.8.0-py3-none-any.whl \
  "https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl"
curl -sL -o _build/html/lite/extra-wheels/fr_core_news_md-3.8.0-py3-none-any.whl \
  "https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.8.0/fr_core_news_md-3.8.0-py3-none-any.whl"
```

`01_spacy_basics.ipynb` resolves this URL from the page's own location at runtime (see [`src/install_pyodide.py`](src/install_pyodide.py)) rather than a hardcoded domain, so it works the same way locally (`http://localhost:8000/lite/extra-wheels/...`) and once deployed — no edits needed if the site later moves to a different GitHub user/org or repo name.

### 4. Preview locally

```bash
cd _build/html
python3 -m http.server 8000
```

- Jupyter Book: http://localhost:8000/
- JupyterLite (JupyterLab interface): http://localhost:8000/lite/lab/index.html
- A specific notebook directly: http://localhost:8000/lite/lab/index.html?path=notebooks/02_webscraping_basics.ipynb

The book and JupyterLite are two separate builds sharing the same `_build/html/` output directory: JupyterLite alone (steps above) only populates `_build/html/lite/` — `http://localhost:8000/` (the book) will be empty/404 until you also run `jupyter book build --html` (see [Build Jupyter Book](#build-jupyter-book)) at least once.

## Accessing the published site

Every push to `main` triggers [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml), which builds and deploys both the book and JupyterLite to GitHub Pages (repository Settings → Pages → Source must be set to **GitHub Actions**):

- Jupyter Book: https://lillaconte.github.io/cours-data-processing/
- JupyterLite: https://lillaconte.github.io/cours-data-processing/lite/lab/index.html
- Each notebook also carries a "Launch in JupyterLite" badge linking directly to its Lite version.

### If the site moves to a different GitHub user/org or repo name

The wheel/model URLs used inside JupyterLite (in [`src/install_pyodide.py`](src/install_pyodide.py)) are computed from the page's own location at runtime, so they need **no changes**. Only the badge links, which are static markdown and can't be computed at runtime, need updating — one line in this README and one markdown cell per notebook (`01`–`05`):

```
https://img.shields.io/badge/Launch-JupyterLite-F37626?logo=jupyter&logoColor=white)](https://<user>.github.io/<repo>/lite/lab/index.html?path=notebooks/<name>.ipynb)
```

## Citation

```bibtex
@misc{jolivet2024datascrapingprocessing,
  author       = {Jolivet, Vincent},
  contributor  = {Conte, Lilla and Terriel, Lucas and Popineau, Maxime},
  title        = {Data scraping and (pre)processing course},
  year         = {2024-2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/architexte/cours-data-processing}},
  institution  = {École nationale des chartes - PSL},
  note         = {Course materials, École nationale des chartes}
}
```
