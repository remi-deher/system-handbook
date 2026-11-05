# Niri sous Ryoku

Compositeur Niri dans Ryoku ; configuration et raccourcis spécifiques. Cette portée reproduit les neuf rubriques numérotées standard.

## Où chercher

- [01-INSTALLATION/](01-INSTALLATION/README.md)
- [02-SYSTEME/](02-SYSTEME/README.md)
- [03-CONFIGURATION/](03-CONFIGURATION/README.md)
- [04-LOGICIEL/](04-LOGICIEL/README.md)
- [05-SCRIPT/](05-SCRIPT/README.md)
- [06-MAINTENANCE/](06-MAINTENANCE/README.md)
- [07-RESOLUTION/](07-RESOLUTION/README.md)
- [08-SAUVEGARDE/](08-SAUVEGARDE/README.md)
- [09-NOTE/](09-NOTE/README.md)

Voir les [instructions IA](00-AGENTS.md) et [l’index parent](../README.md).

## Configuration Niri observée

`~/.config/niri/config.kdl` inclut notamment `settings.kdl`, `rebinds.kdl`, puis `user.kdl` en dernier. Les deux premiers sont générés par Ryoku ; les adaptations personnelles vont dans `user.kdl`. Vérifier processus, environnement, journaux et ordre des inclusions avant de conclure sur la configuration active. Valider avec `niri validate` avant rechargement.
