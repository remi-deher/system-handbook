# Plex Desktop : carrés blancs pendant le défilement

- Résumé : Plex Desktop Flatpak peut afficher des carrés blancs sur l'interface pendant le défilement sous Linux ; forcer le backend Qt Quick sur OpenGL a supprimé le problème sur cette machine.

- Statut : résolu (confirmé par l'utilisateur).
- Date : 2026-11-06.
- Portée : Arch Linux, client Plex Desktop Flatpak `tv.plex.PlexDesktop`.
- Environnements testés : Plex Desktop 1.115.0 depuis Flathub, runtime Freedesktop 26.08 ; le même serveur Plex fonctionne dans Plex Web.
- Prérequis et exclusions : installation Flatpak de Plex Desktop ; cette procédure ne s'applique pas telle quelle aux versions Snap ou aux autres clients.

## But ou problème

Des rectangles blancs apparaissent par-dessus l'interface et les affiches de Plex Desktop lorsqu'on fait défiler la bibliothèque. Plex Web affiche la même bibliothèque correctement, ce qui oriente vers le rendu du client Desktop plutôt que vers les images ou les métadonnées du serveur.

## Diagnostic

Le problème se manifeste dans Plex Desktop et pas dans Plex Web avec la même bibliothèque. Cela indique un problème de rendu dans le client Desktop ; la cause interne exacte n'a pas été établie. Le fil Plex référencé ci-dessous décrit un symptôme similaire et rapporte que forcer Qt Quick sur OpenGL a aidé plusieurs utilisateurs.

## Procédure

Shell : bash, Arch Linux.

1. Fermer complètement Plex Desktop.
2. Forcer Qt Quick à utiliser OpenGL pour cette application Flatpak, avec un remplacement propre à l'utilisateur :

   ```bash
   flatpak override --user --env=QT_QUICK_BACKEND=opengl tv.plex.PlexDesktop
   ```

3. Relancer Plex Desktop et refaire défiler la bibliothèque.

## Validation

Confirmé par l'utilisateur le 2026-11-06 : après application du remplacement et relance de Plex Desktop, les carrés blancs ont disparu.

## Persistance et maintenance

Le remplacement est enregistré dans la configuration Flatpak propre à l'utilisateur et reste actif après fermeture et relance de Plex Desktop. Il ne modifie ni le serveur Plex ni Plex Web. Pour vérifier sa présence :

```bash
flatpak override --user --show tv.plex.PlexDesktop
```

## Sauvegarde et retour arrière

Pour supprimer le remplacement propre à l'utilisateur, puis relancer Plex Desktop :

```bash
flatpak override --user --unset-env=QT_QUICK_BACKEND tv.plex.PlexDesktop
```

## Références

- [Discussion Plex sur les carrés blancs de Plex Desktop Linux](https://forums.plex.tv/t/weird-white-squares-all-over-the-place-with-latest-version/840690?page=7) : plusieurs utilisateurs rapportent que le backend OpenGL règle le problème ; ce contournement n'a pas fonctionné pour tous.
