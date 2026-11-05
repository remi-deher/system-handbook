# Instructions pour les IA — Workflows

Lire `../../AGENTS.md`, puis `../AGENTS.md` et `README.md` ici.

Les workflows contrôlent la structure, les liens, la politique de chiffrement, les secrets détectables et les tests du validateur. La CI ne reçoit jamais d'identité de déchiffrement et ne déchiffre aucun contenu personnel.

Garder les contrôles stables `validation (ubuntu-latest)` et `validation (windows-latest)` sans filtre de chemin : la protection de `main` doit pouvoir l'exiger à chaque modification. `auto-merge.yml` est la seule exception autorisée à `pull_request_target`, car il utilise le secret `AUTOMATION_TOKEN`. Règles impératives : le workflow et le générateur viennent de `main` ; les fichiers de la branche ne sont lus que comme données par `build-index.py --root` ; le jeton n'est jamais dans l'environnement d'une étape qui lit ces fichiers, il n'est utilisé que pour le `git push` et les appels `gh` ; le checkout de la PR garde `persist-credentials: false` ; seules les PR de branches du dépôt sont traitées. Ne jamais exécuter de script, d'action locale ou de hook provenant de la branche de la PR dans ce workflow. Ne pas utiliser `pull_request_target` pour exécuter du contenu de contribution, ne pas accorder de permissions d'écriture inutiles et ne pas publier de rapports contenant des secrets. Épingler les dépendances et documenter leurs mises à jour.
