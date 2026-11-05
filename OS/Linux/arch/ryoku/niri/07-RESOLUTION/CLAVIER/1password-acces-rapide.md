# Raccourci d'accès rapide 1Password sous Niri

Résumé : Sous Niri (Wayland), Ctrl+Maj+Espace n'ouvre pas l'accès rapide de 1Password car l'application ne peut pas enregistrer de raccourci global ; un raccourci Niri qui lance `1password --quick-access` via un script le ramène sur le bureau actif.

Statut : **résolu et confirmé par l'utilisateur le 5 novembre 2026**.

Date : 2026-11-05.

## Portée

Ryoku avec Niri, session Wayland. Non testé sous Hyprland ni sous X11, où les raccourcis globaux de l'application peuvent fonctionner.

## Environnements testés

- Niri avec session Wayland (`XDG_SESSION_TYPE=wayland`), Arch Linux.
- 1Password `8.12.44-33` (paquet `1password`, installé dans `/opt/1Password`).
- Réglage 1Password `keybinds.quickAccess` = `CommandOrControl+Shift+Space`.

## Problème

Ctrl+Maj+Espace n'ouvre pas la fenêtre « Accès rapide » alors que le raccourci est bien configuré dans 1Password.

## Diagnostic

1. **Pas de raccourci global sous Wayland.** Niri ne fournit pas de raccourcis globaux aux applications : 1Password enregistre son raccourci, mais ne le reçoit jamais. L'option `--quick-access` de la ligne de commande permet de contourner : `/opt/1Password/1password --help`.
2. **Lancer la commande directement ne suffit pas.** Le raccourci Niri fonctionnait une seule fois. Les journaux de 1Password (`~/.config/1Password/logs/`) montraient « Getting suggestions for quick access » à chaque appui : la commande arrivait, mais la fenêtre (`app_id` `com.onepassword.OnePassword`, flottante, 550×412) s'affichait sur un autre bureau que le bureau actif (`niri msg --json windows`).
3. **Comportement de la fenêtre propre à l'OS.** Sous Windows, la fenêtre est compacte et se déplie à la saisie. Sous Wayland, l'application ne peut ni se placer ni se centrer : Niri la traite comme une fenêtre flottante ordinaire. Aucun réglage trouvé dans 1Password pour obtenir l'affichage compact sous Linux ; cette absence n'a pas été confirmée auprès de 1Password.

## Procédure

1. Copier [acces-rapide-1p.sh](acces-rapide-1p.sh) vers `~/.local/bin/1password-quick-access` et le rendre exécutable (`chmod +x`). Il lance `--quick-access`, attend la fenêtre, la déplace sur le bureau actif (`move-window-to-workspace --window-id … --focus false`) puis lui donne le focus (`focus-window --id`). Prérequis : `niri`, `python3`.
2. Ajouter dans le bloc `binds` existant de `~/.config/niri/user.kdl` (un seul bloc `binds` est accepté ; un second provoque « duplicate node `binds` ») :

   ```kdl
   binds {
       Ctrl+Shift+Space { spawn "/home/<utilisateur>/.local/bin/1password-quick-access"; }
   }
   ```

3. Valider et recharger (shell Bash ou fish) :

   ```bash
   niri validate
   niri msg action load-config-file
   ```

`Ctrl+Shift+Space` n'était lié à aucune autre action dans `rebinds.kdl` ni `settings.kdl` sur cette installation.

## Validation

- Configuration Niri valide et rechargée sans erreur.
- Essai réel du script depuis un bureau : la fenêtre « Accès rapide — 1Password » est déplacée sur le bureau actif et reçoit le focus.
- Fonctionnement du raccourci confirmé par l'utilisateur le 5 novembre 2026. Shellcheck non exécuté (shim `mise` sans version).
- Le fichier 1Password `settings.json` contient des étiquettes d'authenticité : ne pas le modifier à la main.

## Persistance et limites

- `user.kdl` est inclus en dernier et n'est pas écrasé par les mises à jour de Ryoku.
- Le chemin `/opt/1Password/1password` et le nom `app_id` peuvent changer selon la version ; réexaminer après une mise à jour majeure.
- Le script utilise l'index du bureau (`idx`) : les bureaux Niri sont dynamiques, il lit donc l'index du bureau focalisé à chaque appel.
- Piste non appliquée : une règle de fenêtre Niri (centrage, sans bordure) pour se rapprocher de l'apparence Windows. Elle ne reproduit pas le dépliage à la saisie.

## Sauvegarde et retour arrière

Sauvegarde locale de `user.kdl` avant modification : `~/.local/state/user.kdl.before-1password`. Pour annuler, retirer la ligne du raccourci dans `user.kdl`, valider et recharger, puis supprimer le script.

## Références

- [raccourcis-azerty.md](raccourcis-azerty.md) : autre fiche sur `user.kdl`.
- `/opt/1Password/1password --help` : option `--quick-access`.
