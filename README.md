# Data scraping and (pre)processing

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Binder](https://static.mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/architexte/cours-data-processing/main)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

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
python3.11 -m venv .venv
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
