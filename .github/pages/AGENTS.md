# Instructions pour les IA — Configuration du site GitHub Pages

Lire `../../AGENTS.md`, puis `../AGENTS.md` et `README.md` ici.

Ce dossier technique ne contient aucune connaissance système : seulement la configuration du site. Ne pas y ajouter de fiche. Garder les dépendances épinglées avec leurs empreintes (`pip install --require-hashes`) et regénérer `requirements.txt` avec uv plutôt que le modifier à la main.

Le site est non indexé par défaut (`robots.txt` écrit par `prepare-site.py` et balise `noindex` dans `overrides/main.html`). Ne pas autoriser l'indexation sans instruction explicite de l'utilisateur : le dépôt décrit une machine personnelle.
