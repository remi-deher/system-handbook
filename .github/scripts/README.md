# Contrôles spécifiques de System Handbook

[check-repository.py](check-repository.py) vérifie les conventions qui sont propres à ce dépôt : guides, numérotation, portées, liens locaux, noms d'objets chiffrés et chiffrement des données de sauvegarde.

Les tests [de structure](test_verifier_structure.py) et [de politique des données](test_verifier_depot.py) valident les cas acceptés et refusés. Aucun secret réel n'est utilisé.

Les vérifications standards et la recherche de secrets sont fournies par **pre-commit** et **Gitleaks**, configurés dans [.pre-commit-config.yaml](../../.pre-commit-config.yaml). Le même ensemble s'exécute en local et dans GitHub Actions ; l'analyse de l'historique s'ajoute en CI. Voir [CONTRIBUTING.md](../../CONTRIBUTING.md).

Pour un contrôle ciblé : `python3 -B .github/scripts/check-repository.py`. Avant initialisation de Git, ajouter `--worktree`.

[build-index.py](build-index.py) génère `INDEX.json`, `INDEX.md` et `llms.txt` à la racine à partir des fiches ; ses tests sont dans [test_build_index.py](test_build_index.py). Il est exécuté par le workflow [auto-merge.yml](../workflows/auto-merge.yml) sur chaque pull request (option `--root`), qui pousse le résultat sur la branche. Il n'y a pas de hook pre-commit : le test vérifie seulement que les fiches produisent un index valide. Il ignore les liens symboliques et les fichiers de plus de 512 Kio.

[prepare-site.py](prepare-site.py) copie les fichiers Markdown, `INDEX.json` et `llms.txt` vers le dossier source du site GitHub Pages, réécrit vers GitHub les liens vers des fichiers absents du site et écrit un `robots.txt` bloquant l'indexation ; ses tests sont dans [test_prepare_site.py](test_prepare_site.py).

Les scripts [test-encryption.sh](test-encryption.sh) (Bash) et [test-encryption.ps1](test-encryption.ps1) (PowerShell) rejouent le chiffrement et le déchiffrement documentés avec des données fictives et une clé age jetable ; ils sont lancés par [encryption.yml](../workflows/encryption.yml). En local sous Linux : `bash .github/scripts/test-encryption.sh` (nécessite `age`, `tar` et `openssl`).
