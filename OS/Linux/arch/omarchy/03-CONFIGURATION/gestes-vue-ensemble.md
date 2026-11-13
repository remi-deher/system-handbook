# Gestes du pavé tactile pour la vue d’ensemble

- Résumé : Un balayage à quatre doigts vers le haut ouvre la vue ScrollOverview de Super+Tab ; vers le bas, il la ferme sur la sélection active.
- Statut : testé et confirmé par l’utilisateur.
- Date : 2026-11-12.
- Portée : Omarchy, Hyprland et plugin ScrollOverview.
- Environnement testé : Omarchy 4.5.0, Hyprland 0.56.2, ScrollOverview 07a944e4d16f, pavé tactile Synaptics 06CB:CEEE.
- Prérequis : plugin ScrollOverview installé et chargé ; configuration Hyprland en Lua.

## Configuration

Dans `~/.config/hypr/input.lua`, ajouter :

```lua
hl.gesture({ fingers = 4, direction = "up", action = hl.plugin.scrolloverview.overview("on all") })
hl.gesture({ fingers = 4, direction = "down", action = hl.plugin.scrolloverview.overview("off") })
```

Le premier geste ouvre la même vue sur tous les écrans que le raccourci personnel Super+Tab. Le second utilise la même fermeture que les touches Entrée et Échap de la vue ; il conserve la sélection active. Les gestes préexistants à trois doigts restent disponibles ; ils sont décrits dans [la fiche disposition défilante](disposition-defilante-niri.md).

Sur la version testée, `overview(...)` fournit une fonction d’action en dehors d’un raccourci clavier. La passer directement à `action` : l’appeler seule à l’intérieur d’une autre fonction de geste ne déclenche pas la vue.

## Validation et maintenance

En shell Bash, recharger la configuration puis vérifier les erreurs :

```bash
hyprctl reload
hyprctl configerrors
```

Le rechargement ne signale aucune erreur et l’utilisateur a confirmé le fonctionnement des deux gestes. Après une mise à jour de Hyprland ou du plugin, vérifier leur compatibilité et refaire un essai réel. Pour annuler cette adaptation, retirer les deux lignes ajoutées puis recharger et vérifier la configuration.

## Références

- [Gestes Hyprland](https://wiki.hypr.land/configuring/core/binds/gestures/)
- [Actions ScrollOverview](https://github.com/yayuuu/hyprland-scroll-overview/wiki/Dispatchers)
