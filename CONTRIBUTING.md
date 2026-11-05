# Contribuer à System Handbook

Ce dépôt public conserve des connaissances, configurations et outils système. Lire [AGENTS.md](AGENTS.md), puis les guides de la branche concernée avant modification.

## Ajouter du contenu

- Choisir la portée et la rubrique adaptées ; enrichir une fiche existante avant de créer un doublon.
- Garder `00-AGENTS.md` et `README.md` dans chaque dossier sous `OS/`, et les noms standard `AGENTS.md` et `README.md` à la racine, sous `OUTILS/` et sous `.github/`.
- Expliquer simplement l’utilité du dossier, où chercher ses informations et comment le maintenir. Actualiser les index lorsque le contenu change.
- Conserver les rubriques numérotées et les portées sans numéro. Les données de sauvegarde sont toujours chiffrées ; toute autre donnée sensible doit l’être aussi.
- Utiliser des objets à noms opaques à l’emplacement choisi et ne jamais publier d’identité privée, de manifeste déchiffré ou de détails confidentiels dans les commits. Lire [CHIFFREMENT.md](CHIFFREMENT.md).

## Contrôle obligatoire

Le workflow [Repository validation](.github/workflows/validation.yml) fournit les contrôles `validation (ubuntu-latest)` et `validation (windows-latest)`. Ils doivent être requis sur `main`, y compris pour l’administrateur. Aucun push direct dans `main` : préparer les changements dans une branche et ouvrir une pull request. Le workflow [auto-merge.yml](.github/workflows/auto-merge.yml) active la fusion automatique ; si les contrôles sont verts, la PR est fusionnée en squash et sa branche supprimée. Aucun nombre d’approbations humaines supplémentaire n’est imposé pour ce dépôt personnel.

Le contrôle s’exécute sans filtre de chemins et sans identité de déchiffrement. Il couvre la structure et tous les guides, les liens locaux, les données sauvegardées, les formats sensibles détectables, l’historique Git avec Gitleaks et les tests du validateur propre au dépôt. Il utilise des dépendances épinglées.

La configuration [.pre-commit-config.yaml](.pre-commit-config.yaml) définit les contrôles communs au poste local et à la CI. Installer les hooks une fois par clone :

```bash
pipx install pre-commit==4.7.0
pre-commit install
pre-commit run --all-files
```

Les hooks standards vérifient YAML, conflits, fins de fichier, espaces et marqueurs de clés privées. Gitleaks inspecte les fichiers courants. Un seul contrôle spécifique vérifie les conventions du dépôt, les liens et la politique des sauvegardes chiffrées ; son code et ses tests sont dans [.github/scripts](.github/scripts/README.md).

GitHub Actions exécute les mêmes hooks et ajoute l’historique complet et les tests du validateur, sous Linux et Windows. Le chiffrement utilise directement age et tar, sans réimplémentation Python. On peut reproduire le scan d’historique localement avec `pre-commit run secrets-history --hook-stage manual --all-files`.

Les hooks ne se déploient pas automatiquement avec un clone et peuvent être désactivés ; la protection de `main` exige donc les deux contrôles serveur `validation` de la matrice Linux/Windows avant fusion. Les clés privées ne sont jamais nécessaires à ces contrôles.

## Index généré

`INDEX.json`, `INDEX.md` et `llms.txt` sont produits par [build-index.py](.github/scripts/build-index.py) à partir du titre, de la ligne `Résumé :`, des lignes `Statut :` et `Date :` et du chemin de chaque fiche. Chaque fiche sous `OS/` et `OUTILS/` doit donc avoir une ligne `Résumé :` juste après son titre. **Ils ne se commitent pas à la main** : le workflow [auto-merge.yml](.github/workflows/auto-merge.yml) les régénère sur chaque pull request et pousse un commit « Mettre à jour l'index » sur la branche, avant la fusion. Faire `git pull --rebase` avant de repousser sur une PR ouverte. Une fiche sans `Résumé :` ou sans titre fait échouer les contrôles requis. `INDEX.json` contient tous les fichiers `.md` ; `INDEX.md` et `llms.txt` sont limités aux fiches, outils, portées et documents généraux. Ne jamais les éditer à la main.

```bash
python3 -B .github/scripts/build-index.py          # régénère en local (facultatif) ; code 1 si des fichiers ont changé
python3 -B .github/scripts/build-index.py --check  # vérifie sans écrire
```

## Contrôles complémentaires

Le workflow [Lint](.github/workflows/lint.yml) vérifie le Markdown, les workflows et les scripts shell. Pour les reproduire en local (bash) :

```bash
npx --yes markdownlint-cli2@0.23.0
uv tool run --from shellcheck-py shellcheck --severity=style .github/scripts/*.sh
bash .github/scripts/test-encryption.sh
```

Le test de chiffrement a besoin de `age`, `tar` et `openssl`. `actionlint` peut se lancer avec `go run github.com/rhysd/actionlint/cmd/actionlint@v1.7.12`. Ces contrôles ne sont pas requis pour fusionner dans `main`.

## Résultat d’un scan

« Aucun secret détecté » signifie seulement qu’aucune règle du scanner n’a trouvé de correspondance dans le périmètre analysé. Ne pas contourner un échec par une exclusion globale ou par l’affichage des valeurs suspectes. Examiner localement, corriger le contenu et, pour un secret réellement exposé, le révoquer ou le renouveler avant toute tentative de nettoyage de l’historique.

Les contrôles ne peuvent pas détecter une information privée quelconque ni vérifier le contenu d’un objet chiffré sans sa clé. Le dépôt ne contient et ne fournit donc jamais la clé privée à GitHub Actions.

## Références

- [Protection des branches GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- [Détection native des secrets GitHub](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enable-secret-scanning).
- [Gitleaks](https://github.com/gitleaks/gitleaks).
