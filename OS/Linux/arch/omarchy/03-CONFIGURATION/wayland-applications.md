# Applications Wayland et échelle

- Résumé : Omarchy privilégie Wayland pour les applications compatibles ; Plex Desktop Flatpak utilise Wayland natif sans facteur Qt supplémentaire sur cette machine.
- Statut : Plex testé et taille confirmée ; répétition de Tab apparemment corrigée.
- Date : 2026-11-11.
- Portée : Arch Linux, Omarchy, Hyprland 0.56.2 et Plex Desktop Flatpak 1.115.0.
- Prérequis : session Wayland et application compatible ; XWayland reste nécessaire pour les logiciels qui ne prennent pas en charge Wayland.

## Diagnostic et configuration

La session privilégie déjà Wayland pour GTK, Qt, Firefox et Electron, avec repli lorsque disponible. Contrôler les fenêtres ouvertes avec `hyprctl clients -j` : `xwayland: false` signifie Wayland natif. Cela ne garantit pas le comportement des applications fermées ou futures.

Plex utilisait XWayland et sa sélection avançait parfois toute seule lorsqu’il recevait le focus après Alt+Tab ou Super+Tab. En mode plein écran, le redimensionnement était aussi annulé ; sortir du plein écran a résolu ce symptôme. Le passage à Wayland semble avoir corrigé la répétition, sans établir sa cause exacte. L’utilisateur a confirmé que la taille était correcte après suppression du facteur Qt 1,25.

## Procédure

Dans bash, pour Plex Flatpak, fermer puis relancer l’application après :

```bash
flatpak override --user --socket=wayland --env=QT_QPA_PLATFORM=wayland tv.plex.PlexDesktop
flatpak override --user --unset-env=QT_SCALE_FACTOR tv.plex.PlexDesktop
```

Conserver `QT_QUICK_BACKEND=opengl`, utilisé pour le [problème de carrés blancs](../../07-RESOLUTION/LOGICIEL/plex-desktop-carres-blancs-defilement.md). Le réglage d’écran Hyprland 1,33 reste actif et distinct d’un facteur par application. Le zoom GeForce NOW reste à évaluer séparément : son passage en Wayland natif n’a pas été validé.

## Validation et retour arrière

Plex a été observé avec `xwayland: false` ; l’utilisateur indique que la taille est parfaite et que le problème de Tab semble corrigé. Les autres fenêtres ouvertes étaient natives au moment du contrôle.

Pour retirer le forçage Wayland de Plex, puis relancer :

```bash
flatpak override --user --unset-env=QT_QPA_PLATFORM --nosocket=wayland tv.plex.PlexDesktop
```

Si la taille redevient trop petite sous XWayland, voir [l’ancienne configuration Plex](../../07-RESOLUTION/LOGICIEL/plex-desktop-echelle-xwayland.md).
