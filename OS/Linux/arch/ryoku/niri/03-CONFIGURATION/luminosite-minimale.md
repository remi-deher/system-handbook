# Limiter la luminosité des touches sous Niri

Résumé : Fixer à 1 % la luminosité minimale de l'écran intégré et employer des pas de 1 % sous 5 %, puis des multiples de 5 %, avec les touches multimédias sous Niri.

- Statut : testé.
- Date : 2026-11-13.
- Dernière vérification : 2026-11-13 ; noyau Linux 7.3.4-arch1-1, Niri 26.04, Ryoku 1.0.9.r6109.g08ff328, brightnessctl 0.5.
- Portée : Arch Linux, Ryoku et Niri ; écran intégré.
- Environnement testé : portable Intel à écran eDP, Bash, rétroéclairage `intel_backlight` (96 000 niveaux).
- Prérequis : `brightnessctl`, `ryoku-hw-backlight`, `flock`, Niri et les droits habituels d'accès au rétroéclairage. Le traitement des écrans externes nécessite `ddcutil` et DDC/CI.

## But et diagnostic

La commande Ryoku des touches de luminosité peut descendre sous 1 %, ce qui peut rendre l'écran illisible. Sur la version testée, les curseurs Ryoku examinés limitaient déjà l'écran intégré à 1 %, mais les touches utilisaient une commande distincte. Ce réglage concerne les touches, pas toutes les applications susceptibles de modifier le rétroéclairage.

À la baisse, les pas sont de 5 % jusqu'à 5 %, puis de 1 % jusqu'à 1 %. Si un pas de 5 % dépasserait le seuil, il s'arrête à 5 %. À la remontée, les pas sont de 1 % jusqu'à 5 %, puis rejoignent le multiple de 5 % suivant : 4 → 5 → 10 → 15 %. Les écrans externes gardent les pas relatifs de la commande Ryoku d'origine ; la limite de 1 % ne leur est pas appliquée.

## Installation

Le [script joint](luminosite-minimale.sh) est une copie adaptée de `ryoku-cmd-brightness` de la version testée. Comparer la commande installée à cette version avant utilisation : une mise à jour Ryoku peut avoir modifié le traitement des écrans externes. Il ne faut pas modifier la commande fournie par le paquet.

En Bash, depuis le dossier contenant cette fiche, installer le script dans un emplacement personnel après avoir vérifié qu'il ne remplace aucun fichier existant :

```bash
ryoku owner "$HOME/.local/bin/ryoku-brightness-min"
test ! -e "$HOME/.local/bin/ryoku-brightness-min" && install -D -m 755 luminosite-minimale.sh "$HOME/.local/bin/ryoku-brightness-min"
```

Vérifier `ryoku owner "$HOME/.config/niri/user.kdl"`, puis ajouter les deux raccourcis ci-dessous au bloc `binds` personnel existant. La commande `sh` développe `$HOME` à l'exécution ; elle ne dépend donc pas du nom du compte. Conserver les autres raccourcis personnels.

```kdl
XF86MonBrightnessUp allow-when-locked=true { spawn "sh" "-c" "exec \"$HOME/.local/bin/ryoku-brightness-min\" +5"; }
XF86MonBrightnessDown allow-when-locked=true { spawn "sh" "-c" "exec \"$HOME/.local/bin/ryoku-brightness-min\" -5"; }
```

Vérifier la configuration avec `niri validate`. Sur la session testée, Niri recharge automatiquement le fichier après enregistrement. Vérifier les touches après validation ; en cas d'erreur, restaurer les lignes précédentes.

## Validation et limites

La syntaxe du script et la configuration Niri active ont été validées. Des essais réels sur l'écran intégré ont donné 4 → 5 → 10 → 15 % à la remontée, 10 → 5 → 4 % à la baisse et 1 → 1 % à la baisse. La luminosité initiale a été restaurée. Les raccourcis ci-dessus avec `sh -c` sont une variante portable de ceux testés avec un chemin absolu ; ils n'ont pas été essayés en session. Les écrans externes n'ont pas été testés.

## Persistance et retour arrière

Le script personnel et `user.kdl` persistent indépendamment des fichiers fournis par Ryoku. Cette copie ne reçoit pas automatiquement les corrections de la commande Ryoku : la comparer après mise à jour, notamment pour la prise en charge des écrans externes. Le minimum est calculé en arrondissant 1 % au niveau matériel supérieur ; son rendu visuel dépend de l'écran.

Pour revenir aux raccourcis Ryoku, retirer les deux lignes ajoutées dans `user.kdl`, valider avec `niri validate`, puis supprimer le script personnel après vérification qu'il ne sert plus. Restaurer d'éventuels raccourcis personnels préexistants.
