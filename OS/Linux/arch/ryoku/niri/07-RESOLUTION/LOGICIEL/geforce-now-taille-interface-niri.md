# GeForce NOW : taille de l’interface sous Niri

- Résumé : sous Niri, GeForce NOW Flatpak tourne par XWayland ; un zoom CEF de 125 % agrandit son interface ; aucun banding lié à la profondeur de surface n’a été établi pour ce client.
- Statut : testé (zoom appliqué, effet visuel non encore confirmé par l’utilisateur).
- Date : 2026-11-16.
- Dernière vérification : 2026-11-16 ; GeForce NOW 2.0.90.126 (Flatpak, runtime Freedesktop 24.08), Niri 26.04, Mesa 26.1.8 (Flatpak).
- Portée : Arch Linux, Ryoku, Niri ; GeForce NOW Flatpak `com.nvidia.geforcenow`.
- Environnements testés : écran 1920 × 1200, échelle Niri 1,25.
- Prérequis et exclusions : avoir lancé le client au moins une fois ; 125 % est une préférence de l’utilisateur.

## But ou problème

Agrandir l’interface de 25 % et vérifier si le défaut RGB565 de Plex touche aussi ce client.

## Diagnostic

- Le client utilise CEF avec `--use-angle=gl-egl` et le backend Ozone X11 (XWayland). Le journal de Chromium ne donne pas la profondeur de surface ; elle n’a pas été mesurée. Chromium choisit normalement du 8 bits, et le test xcb de Plex a donné du 8/8/8, mais ce n’est pas une preuve pour GeForce NOW.
- Les préférences CEF ne contenaient plus de zoom (réglage Omarchy du 2026-11-10 perdu) ; l’interface était à 100 %.

## Procédure

Procédure de [la fiche Omarchy](../../../omarchy/07-RESOLUTION/LOGICIEL/geforce-now-interface-trop-petite.md) avec le facteur `1.25` au lieu de `1.5` (niveau CEF enregistré : `ln(1,25)/ln(1,2)` ≈ 1,224). Fermer le client avant (`flatpak kill com.nvidia.geforcenow`), sauvegarder `Preferences`, puis relancer.

## Validation

Valeur écrite et relue dans `Preferences`. L’aspect visuel et l’absence de banding en session de jeu n’ont pas été vérifiés.

## Persistance et maintenance

Une mise à jour ou une réinitialisation du cache CEF peut effacer le zoom, comme observé entre le 2026-11-10 et le 2026-11-16.

## Sauvegarde et retour arrière

Sauvegarde `Preferences.bak-2026-11-16` à côté du fichier (`~/.var/app/com.nvidia.geforcenow/.local/state/NVIDIA/GeForceNOW/CefCache/Default/`). La restaurer client fermé.
