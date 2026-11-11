# Instructions pour les IA — Notes et outils des systèmes

## Mission et points d’entrée

Ce dépôt est la mémoire technique de l’utilisateur pour Linux et Windows : notes, résolutions, scripts, configurations, logiciels, installation, maintenance et sauvegarde. Lire `README.md` et `AGENTS.md` à la racine, puis les `00-AGENTS.md` de tous les parents sous `OS/` jusqu’au dossier cible. Consulter les index `README.md` correspondants. Lire `CHIFFREMENT.md` avant tout traitement de données sensibles ou de données de sauvegarde.

## Arborescence et nommage obligatoires

- À la racine, `OS/` contient les connaissances système, `OUTILS/` les outils communs et `.github/` la CI. Aucun de ces deux dossiers techniques ne constitue une portée OS. Les fichiers généraux `README.md`, `AGENTS.md`, `CHIFFREMENT.md`, `CONTRIBUTING.md`, `MODELE-FICHE.md`, les index générés `INDEX.json`, `INDEX.md` et `llms.txt`, et les fichiers de configuration Git restent à la racine. Un éventuel `.git/` est un répertoire interne de Git.
- `OS/` contient uniquement les regroupements `Linux/` et `Windows/`, et leurs guides. `OS/Linux/` contient les portées `arch/`, `ubuntu/`, `fedora/` et `debian/`, et ses guides.
- Les regroupements racine, `OS/`, `OS/Linux/` et les dossiers techniques `OUTILS/` et `.github/` ne reproduisent pas les neuf rubriques. `OS/Windows/` est une portée système et possède les rubriques.
- Les portées (distribution, environnement, compositeur, logiciel ou machine) portent un nom en minuscules : `arch`, `ryoku`, `omarchy`, `niri`, `hyprland`, `git`, etc. Les noms `OS`, `Linux` et `Windows` sont les noms fixes des niveaux supérieurs.
- Les dossiers qui ne sont pas des portées sont en MAJUSCULES. Les rubriques fixes sont numérotées avec les mêmes numéros partout ; les catégories (`CLAVIER`, `MACHINES`) et dossiers techniques (`HOOKS`, `COFFRE`) sont en majuscules sans numérotation supplémentaire imposée.

| Rubrique fixe | Contenu |
| --- | --- |
| `01-INSTALLATION/` | Installer, reconstruire et migrer |
| `02-SYSTEME/` | Fonctionnement, services, matériel et réglages |
| `03-CONFIGURATION/` | Configurations de référence |
| `04-LOGICIEL/` | Documentation par application |
| `05-SCRIPT/` | Outils exécutables documentés |
| `06-MAINTENANCE/` | Entretien et mises à jour |
| `07-RESOLUTION/` | Problèmes et solutions par catégorie |
| `08-SAUVEGARDE/` | Sauvegarde, archivage, rétention et restauration |
| `09-NOTE/` | Connaissances et observations |

- Chaque nouvelle portée sous `OS/` reproduit ces neuf rubriques et leurs guides, même si elles ne contiennent pas encore de fiche technique.
- Ne pas recréer récursivement les rubriques dans une rubrique, une catégorie ou un dossier technique. Par exemple, `07-RESOLUTION/CLAVIER/` reçoit des fiches et non neuf autres rubriques.
- À la racine et dans les dossiers techniques `OUTILS/` et `.github/`, conserver `AGENTS.md` et `README.md` comme points d’entrée standard. À partir de `OS/`, chaque dossier possède obligatoirement `00-AGENTS.md` et `README.md`. Une résolution correspond à un fichier `<sujet>.md`, pas un dossier par résolution.
- Les fichiers techniques et fiches peuvent garder des noms en minuscules avec tirets. Les fichiers confidentiels chiffrés doivent avoir un nom opaque aléatoire.
- Ne pas réintroduire les anciennes rubriques OS à la racine. Les outils communs vont dans `OUTILS/`, les contrôles techniques dans `.github/` et les scripts spécifiques dans leur portée. Ne pas présenter les squelettes d’autres OS comme des validations.

## Nomenclature stricte sous OS

L’ordre de lecture et le tri par nom sont organisés ainsi dans chaque dossier sous `OS/` :

1. `00-AGENTS.md` : instructions IA locales ; lire également tous les guides parents.
2. `README.md` : index et navigation du dossier.
3. `01-INSTALLATION/` à `09-NOTE/` : rubriques utiles numérotées en MAJUSCULES, aux niveaux de portée concernés.
4. Sous-portées en minuscules et sans numéro : `ryoku/`, `omarchy/`, `niri/`, `hyprland/`, etc.

- Cette règle commence dans `OS/` et s’applique à tous ses descendants, y compris les rubriques, catégories et dossiers techniques ; les regroupements ne reproduisent toujours pas les neuf rubriques.
- Sous `OS/`, ne pas ajouter de `AGENTS.md`, `00-README.md`, `01-AGENTS.md` ou index concurrent. Les deux noms réservés sont exactement `00-AGENTS.md` et `README.md` : seul le guide IA est numéroté, le README garde son nom standard pour son affichage automatique sur GitHub.
- Les fichiers `00-AGENTS.md` sont à lire explicitement : les outils ne doivent pas supposer qu’ils sont automatiquement chargés comme des guides standard. Les `README.md` ne sont pas numérotés afin que GitHub les affiche automatiquement. Le présent `AGENTS.md` racine prescrit leur lecture.
- À chaque nouveau dossier, créer les deux guides numérotés, préciser le rôle (portée, rubrique, catégorie ou dossier technique) et mettre à jour les index parents.
- Lors d’un déplacement ou renommage, corriger les liens et toutes les références aux guides parents, en conservant les noms standard uniquement pour la racine.
- Maintenir la séparation entre navigation par sous-portées et rubriques utiles. Ne pas numéroter une portée ni transformer un dossier de navigation en rubrique.

## Portée, recherche et réutilisation

0. **Commencer par l’index** : `INDEX.md` (lisible) liste les fiches, les outils, les portées et les documents généraux avec titre, résumé, statut et date. `INDEX.json` (structuré, plus volumineux) contient en plus **tous** les fichiers `.md`, guides compris (`kind: "guide"`), avec des mots-clés déduits du chemin ; le filtrer par `kind` plutôt que de le lire en entier. `llms.txt` en donne une version courte avec des liens directs. Ces fichiers sont **générés** : ne jamais les modifier à la main. L’index ne remplace pas la lecture de la fiche trouvée ni des guides `00-AGENTS.md` de sa branche.
1. Identifier OS, distribution, environnement, compositeur, logiciel et machine.
2. Consulter les rubriques des portées parentes, puis les plus spécifiques. Exemple : `OS/Linux/arch/` → `ryoku/` → `niri/`.
3. Consulter aussi les logiciels et machines pertinents à leur emplacement, actuellement `OS/Linux/arch/04-LOGICIEL/` et `OS/Linux/arch/02-SYSTEME/MACHINES/`.
4. Chercher avec `rg --files` puis `rg -n 'mot-clé'` si les index ne suffisent pas.
5. Réutiliser une ressource parent seulement si ses prérequis conviennent. Un contenu Niri ne devient pas un contenu Hyprland ; un script Arch ou Linux n’est pas automatiquement compatible Windows.
6. Ne pas dupliquer un outil commun : le référencer depuis les autres fiches avec ses prérequis et limites. Le placer dans la portée la plus large réellement justifiée, sans violer la structure des regroupements.

L’héritage est documentaire : aucun script, aucune installation et aucune fusion de configuration ne se déclenchent automatiquement.

## Enrichir la documentation après les interventions

- Chercher la fiche existante avant d’en créer une. Après un travail pertinent autorisé, enrichir les `.md` avec la connaissance utile, la solution finale, les commandes et limites.
- Utiliser `MODELE-FICHE.md` pour une nouvelle fiche : résumé, statut, date, portée, prérequis, versions, diagnostic, procédure, validations, persistance et retour arrière selon le sujet.
- **Chaque fiche commence par une ligne `Résumé :`** (une ou deux phrases) juste après le titre. L’index la reprend telle quelle ; son absence fait échouer le contrôle. **Ne pas régénérer ni commiter l'index** : la CI le fait sur chaque pull request et pousse un commit « Mettre à jour l'index » sur la branche. Après l'ouverture d'une PR, faire `git pull --rebase` avant tout nouveau push pour intégrer ce commit. Pour consulter un index à jour en local, `python3 -B .github/scripts/build-index.py` le régénère sans rien envoyer.
- Distinguer hypothèse, proposition, validation syntaxique, simulation et essai réel. Écrire « confirmé par l’utilisateur » uniquement après confirmation effective.
- Documenter les scripts et configurations ajoutés ; mettre à jour les index et les guides parents concernés. Préserver les changements personnels.
- Garder une procédure finale cohérente ; retirer les commandes abandonnées du parcours principal. Expliquer une ancienne erreur seulement si cela aide le diagnostic.
- Écrire en français, employer des liens relatifs et préciser le shell et la plateforme des commandes. WSL ne valide pas Windows natif.

## Chiffrement indépendant de l’emplacement

- Pour tout nouveau chiffrement, utiliser uniquement une phrase secrète avec `age -p` : aucun fichier d’identité ni destinataire à clé publique. La phrase secrète est saisie de façon interactive et ne figure jamais dans le dépôt, les commandes ou les journaux.

- Tout fichier ou dossier peut être chiffré, quelle que soit sa fonction : pièce jointe de résolution, configuration, note ou sauvegarde.
- Un objet chiffré peut rester dans la rubrique appropriée, par exemple `07-RESOLUTION/CLAVIER/` ou `03-CONFIGURATION/`. Aucun coffre central n’est obligatoire ; un dossier `COFFRE/` est facultatif.
- Les contenus sensibles doivent être chiffrés **avant l’ajout à Git**, même si le dépôt est privé. Conserver contenu, noms et chemins d’origine dans le chiffrement ; employer un nom aléatoire `<32-caractères-hex>.age`.
- Les fiches lisibles peuvent utiliser un lien neutre « Pièce chiffrée », sans nom original ni description confidentielle. L’emplacement et le lien révèlent le contexte : si cette association est sensible, choisir un emplacement moins révélateur et garder la correspondance chiffrée.
- Ne pas mettre dans le dépôt de manifeste déchiffré, secret en clair, identité privée, référence d’accès ou indication du fournisseur de stockage privé.
- Ne jamais afficher une clé privée ou une valeur secrète dans les conversations, sorties d’outils, arguments de commande ou journaux. Ne jamais demander de coller une phrase secrète dans les échanges.
- Une nouvelle phrase secrète ne permet pas de déchiffrer les anciens objets ; conserver les moyens de récupération nécessaires à l’historique.
- Déchiffrer dans un nouveau dossier privé hors dépôt, vérifier puis appliquer uniquement les changements demandés. Ne pas écraser automatiquement les configurations actives.
- La taille, le contexte du dossier, le nombre d’objets et les dates de commits restent visibles. Ne pas promettre leur masquage.

## Sauvegardes obligatoirement chiffrées

- `08-SAUVEGARDE/` est réservé à une action de sauvegarde/archivage, sa stratégie, ses contrôles, sa rétention et sa restauration.
- Toutes les données de sauvegarde sont chiffrées, même si leur contenu n’est pas considéré sensible. Seules les fiches de procédure et les guides Markdown restent lisibles dans cette rubrique. Ranger les outils et exemples dans les rubriques adaptées et les référencer.
- Une configuration ou une résolution ne devient pas une sauvegarde parce qu’elle est chiffrée. Elle garde son emplacement fonctionnel.
- Vérifier le déchiffrement avant de déclarer un objet récupérable ; un succès de chiffrement ne prouve pas à lui seul la disponibilité de la phrase secrète.

## Vérification, outils et limites

- Les commandes natives de chiffrement sont documentées dans `OUTILS/CHIFFREMENT/`, en variantes Linux et Windows. Les contrôles reposent sur `.pre-commit-config.yaml` et un seul validateur spécifique dans `.github/scripts/`. Consulter `CONTRIBUTING.md` pour les exécuter.
- Les hooks pre-commit exécutent les contrôles partagés avec la CI, dont les données sous `08-SAUVEGARDE/`. Les activer avec `pre-commit install` ; ils ne détectent pas tous les secrets possibles.
- Après déplacement : vérifier liens, guides parents, commandes, chemins techniques, scripts et adaptateurs locaux concernés.
- Effectuer les tests pertinents lorsqu’un script ou un correctif change. Ne pas relancer des tests sans rapport pour une modification purement documentaire.
- Une demande documentaire ne demande pas de reconfigurer la machine. Les commandes des fiches ne sont pas des instructions à exécuter spontanément.
- Ne pas créer de dépôt distant, publier ou pousser sans instruction de l’utilisateur. Un push de branche et l’ouverture d’une PR ne sont faits que sur demande ; la fusion elle-même est automatique.

## Compte rendu

Indiquer brièvement les fichiers modifiés, validations effectuées et limites restantes, avec un lien vers les fiches utiles.

## CI et publication

- **Aucun push direct dans `main`**, même pour une correction de documentation. Créer une branche, commiter, la pousser et ouvrir une pull request. Le workflow `auto-merge.yml` active la fusion automatique : un job régénère d'abord l'index sur la branche (commit « Mettre à jour l'index »), puis si `validation (ubuntu-latest)` et `validation (windows-latest)` sont verts, GitHub fusionne en squash et supprime la branche. Les PR en retard sur `main` sont mises à jour automatiquement. Si la CI est rouge, corriger dans la même branche ; ne pas contourner la protection ni la désactiver.
- Le dépôt cible est public : aucune donnée confidentielle non chiffrée ne doit être ajoutée. Aucune phrase secrète ne doit être publiée.
- Les contrôles GitHub Actions `validation (ubuntu-latest)` et `validation (windows-latest)` doivent réussir avant fusion dans `main`. Il vérifie tous les dossiers, les guides, les liens, la politique de chiffrement, l’historique avec Gitleaks et les tests du validateur spécifique.
- Respecter les guides standard dans `OUTILS/` et `.github/` et les guides `00-` sous `OS/`. Ne pas ajouter de doublons pour satisfaire artificiellement le contrôle.
- Ne pas affaiblir les contrôles ou ajouter d’exclusion globale de détection pour faire passer une CI. Identifier et corriger la cause, sans publier les valeurs détectées.
- Une CI verte signifie « aucun secret détecté par les contrôles utilisés », pas une garantie absolue d’absence de données sensibles. Le chiffrement avant ajout et la revue humaine restent nécessaires.
