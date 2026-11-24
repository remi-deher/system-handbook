# Plex Desktop : banding vidéo et interface (surface RGB565 sous Wayland)

- Résumé : sous Niri, Plex Desktop en Wayland natif crée une surface OpenGL en RGB565 (16 bits) et affiche du banding partout, même quand mpv et VLC sont propres ; le lancer avec `QT_QPA_PLATFORM=xcb` donne une surface 8/8/8 et supprime le banding.
- Statut : résolu (confirmé par l’utilisateur).
- Date : 2026-11-16.
- Dernière vérification : 2026-11-16 ; Plex Desktop 1.115.0 (paquet Arch `plex-desktop`), Niri 26.04, noyau 7.3.4-arch1-1, Mesa 26.2.7.
- Portée : Arch Linux, Ryoku, Niri ; Plex Desktop installé par le paquet `plex-desktop` (`/opt/plex-desktop`, `/usr/bin/Plex`).
- Environnements testés : portable avec GPU Intel Iris Xe et écran interne 8 bits de 1920 × 1200 (échelle Niri 1,25) ; contenu HEVC 10 bits.
- Prérequis et exclusions : Plex lancé par le paquet natif (pas le Flatpak) ; XWayland disponible. Ne règle pas un banding présent dans la source.

## But ou problème

Banding marqué dans les dégradés sombres de la vidéo et dans l’interface de Plex. Le même fichier lu dans mpv et dans VLC est propre. Le même défaut n’existe pas sous Windows.

## Diagnostic

- Le journal de Plex (`~/.local/share/plex/Logs/Plex.log`) indique `redBufferSize 5, greenBufferSize 6, blueBufferSize 5` pour le contexte OpenGL en Wayland natif : la fenêtre est en RGB565.
- Les options mpv de Plex (`~/.local/share/plex/mpv.conf` : `deband`, `dither-depth=8`, `dither=fruit`) sont bien lues, mais s’appliquent avant la surface de la fenêtre et ne peuvent pas compenser du 5/6/5. Elles n’ont rien changé.
- Essais de lancement : `QT_QPA_PLATFORM=xcb` donne `8/8/8` ; `QT_QPA_PLATFORM=wayland` avec `QSG_RHI_BACKEND=opengl` reste en `5/6/5`.
- Cause du choix 5/6/5 côté Qt/EGL non établie ; aucun réglage de Plex pour la profondeur n’a été trouvé.

## Procédure

Shell : bash. Créer un lanceur utilisateur qui surcharge celui du paquet :

```bash
cat > ~/.local/share/applications/tv.plex.PlexDesktop.desktop <<'DESK'
[Desktop Entry]
Type=Application
Name=Plex
Comment=Plex client for desktop computers
Exec=env QT_QPA_PLATFORM=xcb QT_SCALE_FACTOR=1 Plex
Icon=tv.plex.PlexDesktop
Terminal=false
Categories=AudioVideo;Player;X-Media;
StartupWMClass=Plex
DESK
update-desktop-database ~/.local/share/applications
```

Fermer Plex, le relancer depuis le menu ou `gtk-launch tv.plex.PlexDesktop`. Un lancement direct de `/usr/bin/Plex` garde le rendu Wayland 5/6/5. Sous XWayland, `QT_SCALE_FACTOR=1` a donné une taille correcte sur cette machine ; `1.25` était trop grand.

## Validation

Confirmé par l’utilisateur le 2026-11-16 : le banding a disparu après lancement par le lanceur. La profondeur 8/8/8 a été lue dans le journal de Plex.

## Persistance et maintenance

Le lanceur utilisateur survit aux mises à jour du paquet, mais masque un changement de lanceur du paquet. Revérifier la ligne `redBufferSize` du journal après une mise à jour de Plex ou de Qt : une version future peut corriger le choix 5/6/5 en Wayland natif.

## Sauvegarde et retour arrière

Supprimer `~/.local/share/applications/tv.plex.PlexDesktop.desktop` pour revenir au lanceur du paquet. `mpv.conf` n’a pas besoin d’être modifié pour cette résolution.

## Références

- [Plex Desktop : configuration Wayland (Omarchy)](../../../omarchy/03-CONFIGURATION/wayland-applications.md) : ancienne fiche Flatpak sous Hyprland, à ne pas appliquer telle quelle sur cette machine.
- [Plex Desktop : carrés blancs pendant le défilement](../../../../07-RESOLUTION/LOGICIEL/plex-desktop-carres-blancs-defilement.md).
