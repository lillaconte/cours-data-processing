"""JupyterLite-only setup helpers.

Each function below installs the packages a specific notebook needs to run
in the browser (JupyterLite/Pyodide). They are all no-ops in a regular
Python environment (Jupyter Book, JupyterLab, venv, conda, uv...), so this
module is safe to import unconditionally from any notebook or context.

Usage, in a notebook's first code cell (after the "Launch in JupyterLite"
badge) — this file lives in src/, a sibling folder of notebooks/. Under
JupyterLite, `sys.path.insert(0, "../src")` is NOT reliable: it works on a
real filesystem (desktop Jupyter), but JupyterLite's browser-side "Drive" is
an API-backed virtual filesystem that Python's import machinery cannot
reliably list/traverse to discover a sibling module — this fails with
`ModuleNotFoundError: No module named 'install_pyodide'` even though the
file is really there. Fetching it over HTTP instead sidesteps that
entirely (the same kind of mechanism piplite already uses to fetch wheels,
which is why that part always worked):

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

Note: each notebook opened in JupyterLite runs in its own, isolated kernel
(a fresh Python interpreter) — installing packages in one notebook does not
make them available in another. There is no "install once for the whole
site" shortcut; every notebook that needs extra packages must call the
relevant function itself. These calls are cheap and safe to leave in place
everywhere: they're no-ops outside JupyterLite.

The wasm wheel/model URLs are computed from the current page location
rather than hardcoded, so this keeps working if the site ever moves to a
different GitHub user/org or repository name.
"""

import sys

IS_LITE = sys.platform == "emscripten"

if IS_LITE:
    import js
    import piplite

    # e.g. "https://<user>.github.io/<repo>/lite/lab/index.html?path=..."
    # -> "https://<user>.github.io/<repo>/lite"
    _LITE_BASE = js.location.href.split("/lite/")[0] + "/lite"
    _EXTRA_WHEELS = f"{_LITE_BASE}/extra-wheels"


async def install_dotenv():
    """For notebooks reading a .env file (02_webscraping_basics.ipynb,
    03_europeana_scraping.ipynb): python-dotenv isn't part of Pyodide's
    built-in package set, unlike e.g. httpx/pandas which auto-install on
    import — it needs an explicit piplite install."""
    if not IS_LITE:
        return
    await piplite.install(["python-dotenv"])


async def install_lyricsgenius():
    """For 02_webscraping_basics.ipynb (Genius API section)."""
    if not IS_LITE:
        return
    await piplite.install(["lyricsgenius"])


async def install_thunderdots():
    """For 04_dts_scraping.ipynb.

    thunderdots declares a spurious `notebook` dependency (never actually
    imported at runtime, but it pulls in pyzmq, which has no WASM build), so
    its real dependencies are installed first and thunderdots itself is
    installed with deps=False to skip that unresolvable dependency.
    """
    if not IS_LITE:
        return
    await piplite.install(["edtf", "h2", "jsonschema", "lxml", "rich", "tqdm", "httpx"])
    await piplite.install(["thunderdots"], deps=False)


async def _install_spacy_core():
    """spaCy + its French/English models, shared by 01_spacy_basics.ipynb
    and the preprocessing section of 02_webscraping_basics.ipynb.

    spaCy's core (and blis/thinc) are Cython/C, so the regular PyPI wheels
    can't run in Pyodide's WASM runtime. These are custom wasm32 wheels
    cross-compiled for this exact Pyodide runtime, hosted same-origin
    because GitHub Releases (where the language models live) doesn't send
    the CORS headers a browser requires for cross-origin fetch(). See
    lite/wasm-wheels/README.md for how they were built and how to rebuild
    them.
    """
    if not IS_LITE:
        return
    await piplite.install(["click"])
    await piplite.install([
        f"{_EXTRA_WHEELS}/murmurhash-1.0.15-cp312-cp312-pyodide_2024_0_wasm32.whl",
        f"{_EXTRA_WHEELS}/cymem-2.0.13-cp312-cp312-pyodide_2024_0_wasm32.whl",
        f"{_EXTRA_WHEELS}/preshed-3.0.13-cp312-cp312-pyodide_2024_0_wasm32.whl",
        f"{_EXTRA_WHEELS}/srsly-2.5.3-cp312-cp312-pyodide_2024_0_wasm32.whl",
        f"{_EXTRA_WHEELS}/blis-1.3.3-cp312-cp312-pyodide_2024_0_wasm32.whl",
        f"{_EXTRA_WHEELS}/thinc-8.3.13-cp312-cp312-pyodide_2024_0_wasm32.whl",
        f"{_EXTRA_WHEELS}/spacy-3.8.13-cp312-cp312-pyodide_2024_0_wasm32.whl",
    ])
    await piplite.install([
        f"{_EXTRA_WHEELS}/en_core_web_md-3.8.0-py3-none-any.whl",
        f"{_EXTRA_WHEELS}/fr_core_news_md-3.8.0-py3-none-any.whl",
    ])


async def install_spacy():
    """For 01_spacy_basics.ipynb: spaCy + models + spacyfishing (entity linking)."""
    if not IS_LITE:
        return
    await _install_spacy_core()
    await piplite.install(["spacyfishing"])


async def install_webscraping_deps():
    """For 02_webscraping_basics.ipynb: dotenv (Genius API key), lyricsgenius,
    and spaCy + models (preprocessing section)."""
    if not IS_LITE:
        return
    await install_dotenv()
    await install_lyricsgenius()
    await _install_spacy_core()


def prompt_secret(var_name, label=None):
    """Get an API key/secret (e.g. GENIUS_CLIENT_ACCESS_TOKEN, WSKEY).

    JupyterLite is a public static site: it can't ship a real .env file
    without leaking the secret to every visitor. Under Lite, this asks the
    student for it instead, with masked input (getpass) so it's never shown
    on screen or saved anywhere — it has to be re-entered in every new
    kernel session. Everywhere else, this is exactly the usual
    `load_dotenv()` + `os.getenv(...)` flow, reading `.env` at the project
    root.
    """
    import os

    if IS_LITE:
        if not os.environ.get(var_name):
            import getpass
            os.environ[var_name] = getpass.getpass(f"{label or var_name}: ")
    else:
        from dotenv import load_dotenv
        load_dotenv()

    return os.environ.get(var_name)
