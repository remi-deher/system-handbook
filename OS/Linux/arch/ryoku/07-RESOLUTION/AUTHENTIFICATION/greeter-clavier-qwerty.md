# Écran de connexion Ryoku en QWERTY au lieu d'AZERTY

- Résumé : l'écran de connexion (greeter weston de SDDM) tape en QWERTY alors que le système est en `fr` ; ajouter `keymap_layout` à la section `[keyboard]` générée par `ryoku-greeter` règle le problème.
- Statut : résolu (confirmé par l'utilisateur) ; la cause exacte reste une hypothèse.
- Date : 2026-11-05.
- Portée : Ryoku, paquet `ryoku-desktop` ; indépendant du compositeur de session.
- Environnements testés : `ryoku-desktop` 1.0.7.r5727.gf7197d7-5, `weston` 15.0.1-3, `sddm` 0.21.0-7, Arch (noyau 7.2.14), Dell Latitude 7440, disposition `fr` sans variante.
- Prérequis et exclusions : droits root. Une mise à jour de `ryoku-desktop` écrase la modification. Non testé avec une variante, des options XKB ou plusieurs dispositions.

## But ou problème

Au démarrage ou après fermeture de session, le champ du mot de passe de l'écran de connexion utilise le QWERTY (la touche `a` produit `q`), alors que la session utilise l'AZERTY.

## Diagnostic

- La disposition système était correcte partout : `localectl` (`VC Keymap: fr`, `X11 Layout: fr`), `/etc/vconsole.conf` et `/etc/X11/xorg.conf.d/00-keyboard.conf`.
- SDDM lance `/usr/share/ryoku/lockscreen/ryoku-greeter` (compositeur weston en mode kiosque). Ce script détecte bien `fr`, mais ne la transmet à weston que par la variable `XKB_DEFAULT_LAYOUT`. La config weston générée (`RYOKU_GREETER_DRYRUN=1 /usr/share/ryoku/lockscreen/ryoku-greeter`) n'avait pas de `keymap_layout`.
- Hypothèse, non prouvée directement : weston 15 ignore `XKB_DEFAULT_LAYOUT` et retombe sur `us`. Elle est cohérente avec le fait que la clé explicite règle le problème, mais aucun test de keymap n'a pu la vérifier.

## Procédure ou utilisation

Shell : bash, sur Ryoku. Dans la fonction `keyboard_ini` de `/usr/share/ryoku/lockscreen/ryoku-greeter`, remplacer la ligne finale :

```diff
-  printf '[keyboard]\nnumlock-on=%s\n\n' "$on"
+  printf '[keyboard]\nnumlock-on=%s\n' "$on"
+  [ -n "${layout:-}" ] && printf 'keymap_layout=%s\n' "$layout"
+  [ -n "${variant:-}" ] && printf 'keymap_variant=%s\n' "$variant"
+  printf '\n'
```

Faire d'abord une copie (`sudo cp -n <fichier> <fichier>.orig`), appliquer la modification avec sudo, puis contrôler :

```bash
bash -n /usr/share/ryoku/lockscreen/ryoku-greeter
RYOKU_GREETER_DRYRUN=1 bash /usr/share/ryoku/lockscreen/ryoku-greeter | sed -n '/\[keyboard\]/,/^$/p'
```

La sortie doit contenir `keymap_layout=fr`. Verrouiller ou fermer la session, ou redémarrer : le greeter ne se recharge pas tout seul. Éviter `systemctl restart sddm` depuis la session, car cela la ferme.

## Validation

Confirmé par l'utilisateur : après la modification, l'écran de connexion tape en AZERTY, et un contrôle avec l'ancien fichier de configuration a été fait. Le contrôle de la config générée par `DRYRUN` a été fait pendant l'intervention.

## Persistance et maintenance

- `ryoku-desktop` possède le fichier : toute mise à jour le remplace. Après une mise à jour, vérifier avec la commande `DRYRUN` ci-dessus et réappliquer si besoin.
- Piste durable : signaler le défaut à Ryoku pour que `keyboard_ini` écrive `keymap_layout`. Le commentaire du script mentionne un correctif antérieur (#224) basé sur `XKB_DEFAULT_LAYOUT`, qui semble insuffisant avec weston 15.

## Sauvegarde et retour arrière

Restaurer la copie : `sudo mv /usr/share/ryoku/lockscreen/ryoku-greeter.orig /usr/share/ryoku/lockscreen/ryoku-greeter`.

## Références

- [Résolution AZERTY des raccourcis sous Niri](../../niri/07-RESOLUTION/CLAVIER/raccourcis-azerty.md) : problème distinct (raccourcis de la session).
