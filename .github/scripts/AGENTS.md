# Instructions pour les IA — Contrôles propres au dépôt

Lire `../../AGENTS.md`, puis `../AGENTS.md` et `README.md` ici.

Ce dossier contient quatre familles de scripts, dont `prepare-site.py` (sources du site GitHub Pages, sans exécution de contenu, liens symboliques ignorés, jamais d'objet chiffré) : le validateur de nomenclature, de guides, de liens et de politique des données (`check-repository.py`), le générateur d'index (`build-index.py`) et les tests de chiffrement de la CI (`test-encryption.sh`, `test-encryption.ps1`), avec les tests Python correspondants. Les contrôles génériques sont confiés aux hooks standards de pre-commit et à Gitleaks ; ne pas réimplémenter ces outils.

`build-index.py` n'écrit que `INDEX.json`, `INDEX.md` et `llms.txt` à la racine et ne lit que les fichiers Markdown ordinaires : il ne touche jamais aux objets chiffrés, ignore les liens symboliques et les fichiers volumineux, et refuse d'écrire dans un lien symbolique. La CI l'exécute avec des droits d'écriture sur des fichiers venant d'une branche : ne jamais affaiblir ces protections, ne jamais lui faire lire autre chose que du Markdown ordinaire ni exécuter du contenu de la branche. Garder sa sortie déterministe (aucune date, tri fixe). Les scripts de test de chiffrement n'utilisent que des données fictives et une clé jetable, jamais `.age-recipients` ni une identité du dépôt.

La configuration `.pre-commit-config.yaml` à la racine est la source commune aux contrôles locaux et à GitHub Actions. Conserver un seul validateur spécifique, sans fournisseur de clé, identité privée ni déchiffrement. Tout ajout de règle doit être justifié par une convention du dépôt et testé avec des données synthétiques. Ne pas contourner une anomalie par une exclusion globale.
