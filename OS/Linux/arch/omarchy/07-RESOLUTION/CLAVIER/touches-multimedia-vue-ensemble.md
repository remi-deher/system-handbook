# Touches multimédias dans la vue d'ensemble

Résumé : Dans la vue Scrolloverview de Hyprland, charger les raccourcis multimédias Omarchy dans le sous-clavier de la vue pour conserver les touches de volume, luminosité et lecture.

- Statut : résolu et fonctionnement confirmé par l'utilisateur le 2026-11-11.
- Date : 2026-11-11.
- Portée : Omarchy, Hyprland avec le plugin Scrolloverview et configuration Lua.

## Diagnostic

La vue ouverte par Super+Tab utilise le sous-clavier `scrolloverview`. Les raccourcis multimédias habituels appartiennent au sous-clavier principal et ne sont donc pas actifs dans cette vue, même si leurs options autorisent leur utilisation sur l'écran verrouillé.

## Correction

Dans `~/.config/hypr/bindings.lua`, ajouter au début de la fonction `hl.define_submap("scrolloverview", function()` :

```lua
-- Keep the standard hardware and media keys available in the overview.
dofile((os.getenv("OMARCHY_PATH") or "/usr/share/omarchy") .. "/default/hypr/bindings/media.lua")
```

Ce fichier Omarchy fournit les commandes de volume, luminosité, rétroéclairage du clavier, pavé tactile et lecture multimédia, avec leurs variantes et options. Il reste géré par le paquet ; une mise à jour de ses raccourcis sera reprise au rechargement. Cette solution suppose que ce chemin et les helpers Omarchy restent disponibles.

## Validation et retour arrière

Sous Linux, recharger et vérifier la configuration :

```bash
hyprctl reload
hyprctl configerrors
hyprctl binds -j | jq '[.[] | select(.submap == "scrolloverview" and (.key | startswith("XF86")))] | length'
```

Le rechargement a réussi sans erreur et 30 entrées XF86 ont été recensées dans le sous-clavier. L'utilisateur a confirmé le fonctionnement des touches dans la vue après correction.

Pour revenir en arrière, retirer les deux lignes ajoutées, puis relancer `hyprctl reload` et `hyprctl configerrors`.
