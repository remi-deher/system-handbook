# Raccourcis AZERTY dans Ryoku / Niri

Statut : **résolu et confirmé par l'utilisateur le 4 novembre 2026**.

Résumé : Les raccourcis Super+Alt et Super+Maj avec la rangée AZERTY déplacent une fenêtre vers un bureau ; ils exigent les noms XKB français et `focus=false` pour Maj dans Ryoku avec Niri.

## Comportement attendu

| Combinaison, rangée supérieure | Action |
| --- | --- |
| Super + Alt + touche 1 à 0 | Déplacer la fenêtre vers le bureau choisi et la suivre |
| Super + Maj + touche 1 à 0 | Déplacer la fenêtre vers le bureau choisi et rester sur le bureau actuel |

La touche `0` correspond au bureau 10. Sans Majuscule, la rangée française produit `& é " ' ( - è _ ç à`.

## Portée

Cette fiche concerne Ryoku avec Niri, Ryoku Settings et la disposition française AZERTY. La capture dépend du Hub Ryoku, et la syntaxe des raccourcis dépend de Niri : ce correctif n'est pas déclaré compatible avec Hyprland, tous les bureaux Ryoku ou tous les Linux. Les versions effectivement observées sont listées ci-dessous.

## Environnement observé

- Ryoku, session Wayland avec Niri.
- Niri `26.04`, commit `8ed0da4`.
- Paquet `ryoku-hub` : `1.0.7.r5727.gf7197d7-1`.
- Disposition XKB `fr`, sans variante explicite.
- Interface Ryoku Settings : Quickshell, configuration `hub`.

## Symptômes et causes

1. **La touche &/1 n'était pas capturée dans les réglages.** `Combos.js` acceptait les chiffres mais ignorait plusieurs symboles de la rangée AZERTY. Le sélecteur des raccourcis groupés `1 … 0` refusait également ces symboles. Verr. Maj. ne constituait pas un contournement fiable.
2. **Super+Maj+1 ne déclenchait pas l'action attendue.** Dans cette version de Niri, le raccourci doit employer le symbole sans Majuscule : `Super+Shift+ampersand`, plutôt que `Super+Shift+1`.
3. **Alt et Maj finissaient par produire la même action.** Une première correction avait attribué le déplacement avec suivi aux deux combinaisons. Le magasin Ryoku contenait aussi la réattribution `SUPER + ALT + {n}` vers `SUPER + SHIFT + {n}`. Il fallait restaurer les combinaisons distinctes et ajouter `focus=false` aux raccourcis avec Maj.

L'hypothèse d'un fichier système écrasant `user.kdl` a été vérifiée puis écartée : le processus utilisait `~/.config/niri/config.kdl`, les journaux confirmaient ce chemin et `user.kdl` était inclus en dernier.

## 1. Corriger la capture dans Ryoku Settings

Fichiers concernés :

- `~/.config/quickshell/hub/Combos.js`
- `~/.config/quickshell/hub/Combos.test.mjs`

Le correctif joint ajoute les noms XKB manquants (`ampersand`, `eacute`, `quotedbl`, etc.), prend en compte les codes des lettres accentuées que Qt normalise en majuscules et accepte les symboles AZERTY dans le sélecteur de famille.

Pour un raccourci individuel, le symbole réel est conservé. Pour une famille, le format numérique `{n}` attendu par Ryoku est conservé. **Ce second comportement ne corrige pas la génération des raccourcis Niri : les adaptations de la section suivante restent nécessaires.**

Sur une installation compatible, après sauvegarde des deux fichiers :

```bash
patch --dry-run -p1 -d "$HOME/.config/quickshell/hub" < ryoku-capture-azerty.patch
patch -p1 -d "$HOME/.config/quickshell/hub" < ryoku-capture-azerty.patch
node --test "$HOME/.config/quickshell/hub/Combos.test.mjs"
```

Ces commandes supposent que le terminal est ouvert dans ce dossier. Si le correctif est déjà appliqué ou si les fichiers ont évolué, examiner les différences au lieu de forcer l'application.

Fermer puis rouvrir Ryoku Settings pour charger le nouveau JavaScript. Enregistrer les modifications en cours avant de fermer : la copie locale du Hub désactive la surveillance automatique des fichiers.

## 2. Corriger les raccourcis Niri

Utiliser `~/.config/niri/user.kdl`, et non les fichiers générés `settings.kdl` ou `rebinds.kdl`.

Exemple pour le bureau 1 :

```kdl
binds {
    Super+Alt+ampersand { move-window-to-workspace 1; }
    Super+Shift+ampersand { move-window-to-workspace 1 focus=false; }
}
```

Correspondance de la rangée :

| Touche | Nom XKB sans Majuscule | Bureau |
| --- | --- | --- |
| 1 | ampersand | 1 |
| 2 | eacute | 2 |
| 3 | quotedbl | 3 |
| 4 | apostrophe | 4 |
| 5 | parenleft | 5 |
| 6 | minus | 6 |
| 7 | egrave | 7 |
| 8 | underscore | 8 |
| 9 | ccedilla | 9 |
| 0 | agrave | 10 |

Le fichier [azerty-niri-user.kdl](azerty-niri-user.kdl) contient la copie finale complète. Il conserve aussi les variantes Super+Alt+Maj déjà présentes, avec suivi. Fusionner les lignes pertinentes dans le fichier personnel, sans écraser les autres règles.

## 3. Supprimer la réattribution conflictuelle

Dans le Hub, restaurer la combinaison par défaut de « Send window to workspace ». La commande utilisée sur cette version était :

```bash
ryoku-hub desktop set-rebind 'SUPER + ALT + {n}' 'SUPER + ALT + {n}'
```

Elle restaure cette entrée sans réinitialiser tous les autres raccourcis. Vérifier que `desktop.keybindRebinds` dans `~/.config/ryoku/desktop.json` ne redirige plus Alt vers Maj. Le champ peut être absent lorsque le dictionnaire est vide.

## 4. Valider et recharger

```bash
niri validate
niri msg action load-config-file
```

Vérifier ensuite avec une fenêtre de test et deux bureaux distincts :

1. Super+Alt+touche du bureau de destination : la fenêtre et le focus doivent changer de bureau.
2. Super+Maj+touche d'un autre bureau : la fenêtre doit partir, et le focus doit rester sur le bureau de départ.
3. Réessayer l'enregistrement dans les réglages avec la rangée supérieure, puis Verr. Maj. activé et désactivé.

Résultats obtenus : 15 tests JavaScript réussis, configuration Niri valide, rechargement sans erreur, comportement final confirmé par l'utilisateur. Le passage des tests unitaires ne garantit pas toutes les variantes de clavier.

## Persistance et limites

- `user.kdl` est le fichier personnel, inclus en dernier ; il n'a pas besoin d'une copie dans `user_edits`.
- Les deux fichiers du correctif de capture ont été copiés dans `~/.config/ryoku/user_edits/quickshell/hub/` pour être réappliqués par Ryoku aux mises à jour.
- Ce mécanisme conserve des fichiers entiers. Comparer aux nouvelles versions amont après mise à jour pour ne pas masquer des corrections officielles.
- Les raccourcis explicites de `user.kdl` ne suivent pas automatiquement les futures réattributions du Hub. Les modifier ensemble si les combinaisons souhaitées changent.
- Cette résolution concerne la disposition française observée et Niri 26.04. Réexaminer le comportement pour une autre variante ou une nouvelle version.

## Sauvegardes et retour arrière

Les sauvegardes de cette intervention sont locales, hors de ce futur dépôt : `~/.local/state/ryoku-azerty-fix/`.

- `Combos.js.before` et `Combos.test.mjs.before` : avant correction de la capture.
- `user.kdl.before-shift-fix` : avant ajout des raccourcis Maj.
- `user.kdl.before-quiet-fix` : avant séparation des actions Alt/Maj.
- `desktop.json.before-quiet-fix` : avant suppression de la réattribution conflictuelle.

Pour annuler la capture, restaurer les deux fichiers JavaScript sauvegardés et retirer ou adapter leurs copies dans `user_edits`, puis rouvrir les réglages. Sur une autre machine, utiliser ses propres sauvegardes.

Pour annuler les raccourcis Niri, retirer ou restaurer uniquement les blocs concernés dans `user.kdl`, puis valider et recharger. Les sauvegardes intermédiaires peuvent contenir les erreurs décrites ci-dessus : les consulter avant restauration. Une restauration complète de `desktop.json` peut écraser d'autres réglages ; préférer modifier la seule entrée de réattribution concernée.

## Références

- [Niri : raccourcis et symboles XKB](https://niri-wm.github.io/niri/Configuration:-Key-Bindings.html). La page décrit aussi des évolutions annoncées pour une version ultérieure ; tenir compte de la version installée.
- `niri msg action move-window-to-workspace --help` : le paramètre `--focus false` conserve le focus sur le bureau d'origine ; son équivalent KDL est `focus=false`.
- `~/.config/ryoku/user_edits/README.md` : fonctionnement des copies persistantes Ryoku sur cette installation.
