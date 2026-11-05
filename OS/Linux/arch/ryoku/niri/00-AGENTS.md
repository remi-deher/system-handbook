# Instructions pour les IA — Niri sous Ryoku

Lire `../../../../../AGENTS.md`, `../../../../00-AGENTS.md`, `../../../00-AGENTS.md`, `../../00-AGENTS.md`, `../00-AGENTS.md`, puis `README.md` ici.

## Utilité

Compositeur Niri dans Ryoku ; configuration et raccourcis spécifiques. Cette portée reproduit les neuf rubriques numérotées standard.

## Maintenir ce dossier

- Chercher d’abord dans l’index local et les portées parentes ; vérifier les prérequis avant réemploi.
- Après une intervention utile, compléter la fiche pertinente ou en ajouter une, préciser les validations réelles et actualiser les index.
- Conserver `00-AGENTS.md` et `README.md`. Les rubriques utiles gardent les numéros `01-` à `09-` en majuscules ; les sous-portées restent en minuscules sans numéro.
- Reproduire les neuf rubriques pour une nouvelle portée seulement, pas dans les catégories ou rubriques.

Toute donnée sensible relève de [la procédure de chiffrement](../../../../../CHIFFREMENT.md). Ne jamais ajouter une identité privée ou un déchiffrement au dépôt.

## Configuration Niri observée

`~/.config/niri/config.kdl` inclut notamment `settings.kdl`, `rebinds.kdl`, puis `user.kdl` en dernier. Les deux premiers sont générés par Ryoku ; les adaptations personnelles vont dans `user.kdl`. Vérifier processus, environnement, journaux et ordre des inclusions avant de conclure sur la configuration active. Valider avec `niri validate` avant rechargement.
