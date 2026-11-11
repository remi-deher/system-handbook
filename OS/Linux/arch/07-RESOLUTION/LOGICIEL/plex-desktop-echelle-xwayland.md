# Plex Desktop : taille et netteté sous XWayland

- Résumé : sous Omarchy et Hyprland, Plex Desktop Flatpak affiché par XWayland peut être trop petit ; un facteur Qt propre à Plex de 1,25 donne une taille et une netteté correctes sur la machine testée.
- Statut : résolu pour Plex (confirmé par l'utilisateur) ; réglage global à étudier.
- Date : 2026-11-10.
- Portée : Arch Linux, Omarchy, Hyprland et Plex Desktop Flatpak `tv.plex.PlexDesktop`.
- Environnements testés : écran 1920 × 1200 avec échelle Hyprland de 1,33, Plex lancé par XWayland.
- Prérequis et exclusions : ce facteur est adapté aux préférences et à l'écran testés ; il ne s'applique pas automatiquement à Steam ou GeForce NOW.

## Diagnostic

Avec `xwayland:force_zero_scaling` activé, les fenêtres XWayland ne sont pas agrandies par le compositeur et Plex était trop petit. L'agrandissement global par le compositeur a rendu son texte moins net. Le facteur Qt propre à Plex permet à l'application de dessiner elle-même à la taille demandée.

## Procédure

Dans un shell bash, pour cette installation Flatpak :

```bash
flatpak override --user --env=QT_SCALE_FACTOR=1.25 tv.plex.PlexDesktop
```

Fermer complètement Plex puis le relancer. Conserver `xwayland:force_zero_scaling` activé pour éviter l'agrandissement supplémentaire par le compositeur. Le réglage Qt Quick OpenGL préexistant reste indépendant ; voir [la fiche sur les carrés blancs](plex-desktop-carres-blancs-defilement.md).

## Validation

L'utilisateur a confirmé le 2026-11-10 que le facteur 1,25 convient pour Plex. Le réglage global XWayland précédent, avec une échelle d'écran de 1,33, manquait de netteté. Steam et GeForce NOW n'ont pas encore été validés avec un réglage individuel.

## Persistance et retour arrière

L'override Flatpak persiste après redémarrage de l'application. Pour le supprimer, puis relancer Plex :

```bash
flatpak override --user --unset-env=QT_SCALE_FACTOR tv.plex.PlexDesktop
```

## Références

- [Documentation Hyprland sur XWayland et HiDPI](https://wiki.hypr.land/configuring/extra/xwayland/) : compromis entre agrandissement par le compositeur et netteté ; réglages propres aux bibliothèques graphiques.
