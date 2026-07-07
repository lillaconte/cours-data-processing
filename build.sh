#!/usr/bin/env bash
#
# Build the Jupyter Book and/or JupyterLite site locally, reproducing the
# steps run by .github/workflows/deploy.yml, so the result can be checked
# before pushing. See README.md for what each step does and why.
#
# Usage:
#   ./build.sh --all              Book + spaCy wasm deps + JupyterLite
#   ./build.sh --only book        Jupyter Book only
#   ./build.sh --only deps        Stage the spaCy wasm wheels + models only
#   ./build.sh --only lite        JupyterLite only (notebooks/data/img/src)
#
#   --serve combines with any of the above: serve _build/html on
#   http://localhost:8000 once the requested build(s) finish.
#
# Examples:
#   ./build.sh --all --serve
#   ./build.sh --only lite --serve
#
# Notes:
#   - "deps" stages the wasm wheels already committed in lite/wasm-wheels/
#     and downloads the spaCy models; it does not recompile spaCy itself
#     (see lite/wasm-wheels/README.md for that, rarely needed rebuild).
#   - "deps" writes into _build/html/lite/extra-wheels/, so run "lite"
#     (or --all) at least once first for it to be useful.

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

MODE=""
SERVE=false

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --all)
      MODE="all"
      shift
      ;;
    --only)
      MODE="${2:-}"
      shift 2
      ;;
    --only=*)
      MODE="${1#--only=}"
      shift
      ;;
    --serve)
      SERVE=true
      shift
      ;;
    -h|--help)
      usage 0
      ;;
    *)
      echo "Argument inconnu : $1" >&2
      usage 1
      ;;
  esac
done

if [ -z "$MODE" ]; then
  echo "Erreur : passez --all ou --only {book|deps|lite}" >&2
  usage 1
fi

case "$MODE" in
  all|book|deps|lite) ;;
  *)
    echo "Erreur : --only doit valoir book, deps ou lite (reçu : $MODE)" >&2
    exit 1
    ;;
esac

build_book() {
  echo "==> Build Jupyter Book"
  if ! command -v jupyter-book >/dev/null 2>&1; then
    echo "jupyter-book introuvable. À installer une fois avec : npm install -g jupyter-book" >&2
    exit 1
  fi
  jupyter-book build --html
}

build_lite() {
  echo "==> Build JupyterLite"
  rm -rf lite_content
  mkdir -p lite_content
  cp -r notebooks lite_content/
  cp -r data lite_content/
  cp -r img lite_content/
  cp -r src lite_content/

  uv run --group lite jupyter lite build --contents lite_content --output-dir _build/html/lite

  rm -rf lite_content .jupyterlite.doit.db
}

build_deps() {
  echo "==> Staging des wheels wasm spaCy + modèles"
  mkdir -p _build/html/lite/extra-wheels
  cp lite/wasm-wheels/*.whl _build/html/lite/extra-wheels/
  curl -sL -o _build/html/lite/extra-wheels/en_core_web_md-3.8.0-py3-none-any.whl \
    "https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl"
  curl -sL -o _build/html/lite/extra-wheels/fr_core_news_md-3.8.0-py3-none-any.whl \
    "https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.8.0/fr_core_news_md-3.8.0-py3-none-any.whl"
}

serve() {
  echo "==> Serveur local sur http://localhost:8000 (Ctrl+C pour arrêter)"
  (cd _build/html && python3 -m http.server 8000)
}

case "$MODE" in
  all)
    build_book
    build_lite
    build_deps
    ;;
  book)
    build_book
    ;;
  lite)
    build_lite
    ;;
  deps)
    build_deps
    ;;
esac

if [ "$SERVE" = true ]; then
  serve
fi
