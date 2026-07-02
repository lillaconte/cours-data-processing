---
title: Introduction
---
 
# Introduction
 
Bienvenue dans ce cours consacré au traitement de données textuelles et à
l’extraction de données sur le Web.
 
Ce Jupyter Book présente progressivement plusieurs méthodes permettant de :
 
- analyser du texte avec spaCy ;
- comprendre les principes fondamentaux du web scraping ;
- construire des scripts de scraping et utiliser des API publiques ;
- découvrir des ressources et des outils complémentaires.
 
## Organisation du cours
 
Le cours est composé de six notebooks principaux.
 
### 1. Text Processing with spaCy
 
Introduction au traitement automatique du langage avec spaCy :
 
- chargement d’un modèle linguistique ;
- tokenisation ;
- lemmatisation ;
- analyse morphosyntaxique ;
- reconnaissance d’entités nommées.
 
### 2. Basics in Web Scraping
 
Présentation des principes essentiels du web scraping :
 
- structure d’une page HTML ;
- requêtes HTTP ;
- extraction de données ;
- sélection d’éléments HTML ;
- export des résultats.

### 3. Use Case: Europeana APIs

Présentation de la suite d'API Europeana (Search API, Annotation API, Fulltext API) :

- récupération des métadonnées descriptives d'objets patrimoniaux ;
- exploration des collections patrimoniales (images et texte ocr).

### 4. Use Case: Text scraping with DTS API

Présentation de l'API DTS et du client Python ThunderDots :

- récupération et l'exploration de collections textuelles ;
- téléchargement de documents ;
- normalisation de métadonnées.

### 5. Bonus: Vibecode your scraping

Présentation d'une approche de scraping assistée par IA :

- utilisation de GPT/Codex à des fins méthodologiques ;
- récupération de données à partir d'un URL ;
- utilisation d'un SPARQL endpoint ;
- moissonnage via un entrepôt OAI-PMH.
 
### 6. Resources and Cool Tools

Cette dernière section rassemble des ressources, bibliothèques et outils utiles
pour poursuivre l’apprentissage.

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