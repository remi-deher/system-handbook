# Configuration du site GitHub Pages

Ce dossier contient la configuration du site MkDocs Material publié par [pages.yml](../workflows/pages.yml) : [mkdocs.yml](mkdocs.yml), les dépendances Python épinglées avec leurs empreintes ([requirements.in](requirements.in) et [requirements.txt](requirements.txt)) et les [modèles de surcharge du thème](overrides/README.md).

Les sources du site sont préparées par [prepare-site.py](../scripts/prepare-site.py) dans `_site-src` (ignoré par Git) et le site construit est écrit dans `_site`. Le site n'est pas indexé par les moteurs de recherche.

Pour régénérer `requirements.txt` après un changement de `requirements.in` : `uv pip compile .github/pages/requirements.in --generate-hashes --python-version 3.13 -o .github/pages/requirements.txt`. Voir les [instructions IA](AGENTS.md) et [l'index parent](../README.md).
