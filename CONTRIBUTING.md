# Contribuer

Guide rapide pour modifier un notebook (ou tout autre fichier) et pousser ses changements.

## 1. Installer l'environnement

Choisissez une seule méthode (voir le [README](README.md#installation) pour le détail des trois) :

```bash
uv sync
```

```bash
# ou avec pip + venv
python3.12 -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Modifier un notebook

```bash
uv run jupyter lab
```

```bash
# ou avec pip + venv (environnement déjà activé)
jupyter lab
```

Ouvrez le notebook dans `notebooks/`, modifiez-le, exécutez les cellules pour vérifier que tout fonctionne (sorties à jour, pas d'erreur).

> Ne modifiez pas `requirements.txt` — c'est le fichier de référence des dépendances, aligné manuellement avec `pyproject.toml` et `environment.yml`.

## 3. Tester en local avant de pousser

- **Le notebook lui-même** : rejouez-le en entier (`Run > Run All Cells`) et vérifiez qu'il tourne sans erreur du début à la fin.
- **Le rendu dans le livre et/ou JupyterLite** (optionnel — le livre si la mise en page/le texte a changé ; JupyterLite seulement si vous touchez à `01_spacy_basics.ipynb`, `02_webscraping_basics.ipynb`, `04_dts_scraping.ipynb` ou `src/install_pyodide.py`) : utilisez [`build.sh`](build.sh) à la racine, qui reproduit exactement ce que fait la CI :

  ```bash
  ./build.sh --all --serve       # tout : livre + JupyterLite, puis ouvre http://localhost:8000
  ./build.sh --only book --serve # juste le livre
  ./build.sh --only lite --serve # juste JupyterLite
  ```

  Détail de chaque étape (et dépannage) dans le [README](README.md#build-the-site-locally-buildsh).

## 4. Pousser ses changements

```bash
git checkout -b ma-modif
git add notebooks/mon_notebook.ipynb
git commit -m "Décrire le changement"
git push -u origin ma-modif
```

Puis ouvrez une Pull Request. Le site (Jupyter Book + JupyterLite) se reconstruit et se publie automatiquement à chaque push sur `main` (voir [.github/workflows/deploy.yml](.github/workflows/deploy.yml)) — pas d'action manuelle nécessaire après la fusion.

## Bon à savoir

- Ne commitez jamais votre fichier `.env` (clé API Genius) — il est déjà ignoré par git.
- Si un notebook produit des sorties volumineuses (images, tableaux longs...), c'est normal qu'elles apparaissent dans le diff : c'est le fonctionnement standard des notebooks Jupyter.
