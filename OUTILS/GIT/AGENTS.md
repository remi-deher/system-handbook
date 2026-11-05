# Instructions pour les IA — Outils Git

Lire `../../AGENTS.md`, `../AGENTS.md` et `README.md`.

Ce dossier regroupe les outils Git communs au dépôt. Le nettoyage des branches distantes est déjà fait par GitHub (voir `.github/workflows/auto-merge.yml`) ; ici on ne traite que le nettoyage local.

Ne jamais supprimer une branche qui contient des commits absents d'une PR fusionnée, ni la branche extraite dans le dépôt principal. Ne lancer `--apply` qu'après une simulation relue, avec l'accord de l'utilisateur : la suppression d'une branche locale est difficile à annuler.
