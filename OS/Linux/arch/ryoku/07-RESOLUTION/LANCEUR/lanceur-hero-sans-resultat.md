# Lanceur Super+Espace sans résultat (variante hero)

Statut : **contournement confirmé par l'utilisateur le 5 novembre 2026 ; cause non identifiée**.

- Résumé : Sous Ryoku (Niri et Hyprland), le lanceur Super+Espace n'affiche aucun résultat avec la variante `hero` ; contournement en passant à la variante `main`, sans cause identifiée.

- Date : 2026-11-05.
- Portée : Ryoku (Niri et Hyprland), lanceur Quickshell (configuration `shell`).
- Environnements testés : Arch Linux, Niri, Quickshell `0.3.2-1`, shell fish ; machine portable Dell. Sous Hyprland, l'utilisateur indique que le correctif fonctionne aussi ; je n'ai pas pu le vérifier moi-même.
- Prérequis et exclusions : variantes disponibles `hero`, `kairos`, `main`, `okshell`, `python`, `spotlight`. Le réglage `launcher.json` et la commande `qs` sont communs à Ryoku ; seul le fichier qui définit le raccourci diffère selon le compositeur.

## But ou problème

Avec Super+Espace, la recherche d'une application n'affichait aucun résultat avec la variante `hero`. L'utilisateur juge cette variante globalement boguée.

## Diagnostic

Vérifié :

- Sous Niri, le raccourci est défini dans `~/.config/niri/rebinds.kdl` : `Super+Space { spawn "ryoku-shell" "launcher"; }`. Sous Hyprland, il passe par la configuration Hyprland de Ryoku (non inspectée).
- La variante active est lue dans `~/.config/ryoku/launcher.json` (clé `variant`).
- Le processus `qs -c shell` avait `XDG_DATA_DIRS` correct, et les entrées `.desktop` existaient. Aucune application n'était masquée (`hiddenApps` vide).
- Les journaux (`qs log -c shell`) ne montraient aucune erreur liée au lanceur, seulement du bruit sans rapport (`MprisPanel`, `AvatarImage`).
- Le code des providers et du dispatcher (`modules/launcher/shared/`) n'a révélé aucun défaut à la lecture.
- Un redémarrage de Quickshell n'a pas résolu le problème.

Non vérifié : la cause dans `hero`. Les tests n'ont pas pu piloter le lanceur de façon fiable, et aucun test d'affichage réel n'a été fait côté assistant.

## Procédure ou utilisation

Passer à la variante `main` (shell : bash ou fish) :

```sh
sed -i 's/"variant": "hero"/"variant": "main"/' ~/.config/ryoku/launcher.json
qs ipc -c shell call theme reload
```

Si le changement n'est pas pris en compte, redémarrer le shell :

```sh
qs kill -c shell; setsid qs -c shell >/dev/null 2>&1 &
```

## Validation

Essai réel par l'utilisateur sous Niri : « ok pour main ». Sous Hyprland, fonctionnement rapporté par l'utilisateur, sans observation de ma part. Aucune validation automatisée.

## Persistance et maintenance

`launcher.json` est un fichier de réglages Ryoku : une mise à jour ou une réapplication du thème peut le réécrire. Vérifier la clé `variant` après une mise à jour.

## Sauvegarde et retour arrière

Revenir à l'ancienne variante en remettant `"variant": "hero"` dans `~/.config/ryoku/launcher.json`, puis recharger comme ci-dessus.

## Références

- [Index des résolutions Ryoku](../README.md)
