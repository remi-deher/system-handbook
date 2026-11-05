# System Handbook

[![Validation Linux et Windows](https://github.com/remi-deher/system-handbook/actions/workflows/validation.yml/badge.svg)](https://github.com/remi-deher/system-handbook/actions/workflows/validation.yml)

[Dépôt public GitHub](https://github.com/remi-deher/system-handbook).

Documentation personnelle des systèmes, configurations, résolutions et outils. Le dépôt `system-handbook` couvre Linux et Windows.

## Navigation

```text
OS/
├── Linux/
│   ├── arch/
│   │   ├── 01-INSTALLATION/
│   │   ├── 02-SYSTEME/
│   │   ├── 03-CONFIGURATION/
│   │   ├── 04-LOGICIEL/
│   │   ├── 05-SCRIPT/
│   │   ├── 06-MAINTENANCE/
│   │   ├── 07-RESOLUTION/
│   │   ├── 08-SAUVEGARDE/
│   │   ├── 09-NOTE/
│   │   ├── omarchy/
│   │   └── ryoku/
│   │       ├── [mêmes neuf rubriques]
│   │       ├── niri/
│   │       └── hyprland/
│   ├── ubuntu/
│   ├── fedora/
│   └── debian/
└── Windows/
    └── [mêmes neuf rubriques]
```

À la racine, les points d’entrée restent `README.md` et `AGENTS.md`. Sous `OS/`, chaque dossier possède `00-AGENTS.md` et `README.md`, suivis des rubriques numérotées puis des sous-portées en tri par nom. Les distributions, environnements et compositeurs gardent un nom en minuscules ; les rubriques fixes sont numérotées et en MAJUSCULES. Les catégories sont aussi en majuscules, par exemple `CLAVIER`.

La racine contient `OS/` pour les connaissances système, `OUTILS/` pour les outils communs et `.github/` pour l’intégration continue, avec les guides et fichiers techniques généraux. Les regroupements `OS/` et `OS/Linux/` ne reproduisent pas les rubriques ; elles commencent aux portées système et se retrouvent dans les portées spécialisées.

## Accès directs

- [Linux](OS/Linux/README.md) : [Arch](OS/Linux/arch/README.md), [Ubuntu](OS/Linux/ubuntu/README.md), [Fedora](OS/Linux/fedora/README.md), [Debian](OS/Linux/debian/README.md).
- [Windows](OS/Windows/README.md).
- [Ryoku](OS/Linux/arch/ryoku/README.md), [Omarchy](OS/Linux/arch/omarchy/README.md).
- [Niri](OS/Linux/arch/ryoku/niri/README.md), [Hyprland](OS/Linux/arch/ryoku/hyprland/README.md).
- [Résolution AZERTY](OS/Linux/arch/ryoku/niri/07-RESOLUTION/CLAVIER/raccourcis-azerty.md).
- [Commandes de chiffrement communes](OUTILS/CHIFFREMENT/README.md).

## Portée et confidentialité

Chercher dans les portées parentes avant les plus spécifiques. L’emplacement ne remplace pas les prérequis et environnements testés. Les squelettes préparés ne constituent pas une validation technique.

Le [chiffrement](CHIFFREMENT.md) s’applique à tout fichier ou dossier, à l’emplacement choisi, sans coffre central imposé. Les noms d’origine sont chiffrés avec le contenu. **Toutes les données de sauvegarde sont obligatoirement chiffrées** ; les procédures Markdown restent lisibles.

Lire les [instructions IA](AGENTS.md), utiliser le [modèle de fiche](MODELE-FICHE.md) et enrichir les index après les interventions utiles. Le dépôt GitHub est public ; les données personnelles restent chiffrées. Aucun push direct dans `main` : toute modification passe par une pull request depuis une branche. Quand les contrôles Linux et Windows sont verts, GitHub fusionne la PR en squash et supprime la branche ; cette règle s’applique aussi à l’administrateur. La détection native des secrets et la protection des pushes sont activées.

## Index

L’[index généré](INDEX.md) liste les fiches, les outils et les portées avec leur résumé, leur statut et leur date. Sa version structurée est [INDEX.json](INDEX.json), qui contient en plus tous les guides (`kind: guide`) et [llms.txt](llms.txt) en donne un résumé court pour les outils d’IA. Ces trois fichiers sont régénérés par la CI à partir des fichiers Markdown (`.github/scripts/build-index.py`) sur chaque pull request ; ne pas les modifier à la main.

## Site

Le contenu est aussi publié sur [GitHub Pages](https://remi-deher.github.io/system-handbook/) (recherche, navigation). Le site n’est pas indexé par les moteurs. Il est reconstruit à chaque fusion dans `main` ; voir les [workflows](.github/workflows/README.md).

## Ordre et nomenclature des guides

Sous `OS/`, les noms sont stricts : `00-AGENTS.md` pour les instructions IA et `README.md` non numéroté pour l’index et son affichage automatique dans GitHub. Les neuf rubriques utiles gardent les préfixes `01-` à `09-` et les sous-portées, comme `omarchy`, `niri` ou `hyprland`, restent sans numéro en minuscules. Les guides racine demandent explicitement aux IA de lire les guides numérotés de toute la branche.

## Contrôles de contribution

Flux unique : créer une branche, commiter, pousser la branche et ouvrir une pull request (`gh pr create`). Le workflow [auto-merge.yml](.github/workflows/auto-merge.yml) régénère l'index sur la branche, active la fusion automatique et met à jour les PR en retard ; une CI rouge bloque la fusion et la branche reste ouverte pour correction.

Lire [CONTRIBUTING.md](CONTRIBUTING.md) et les [workflows de validation](.github/workflows/README.md). Chaque dossier possède ses guides et chaque modification est contrôlée par la CI. Aucun secret détecté ne doit être accepté pour faire passer une modification.

Les contrôles standards sont partagés entre les hooks locaux **pre-commit** et GitHub Actions. Un seul validateur maison couvre les conventions propres à ce dépôt ; voir [CONTRIBUTING.md](CONTRIBUTING.md).
