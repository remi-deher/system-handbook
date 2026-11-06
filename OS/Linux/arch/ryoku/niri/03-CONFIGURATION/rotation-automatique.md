# Rotation automatique de l’écran — Niri

Résumé : sous Ryoku avec Niri, `iio-niri` écoute l’orientation fournie par `iio-sensor-proxy` et applique une transformation à l’écran `eDP-1`. En portrait, un compagnon IPC Niri empile les colonnes simples par paires pleine largeur et restaure leurs largeurs en paysage.

- Statut : rotation automatique et disposition portrait vérifiées par l’utilisateur.
- Date : 2026-11-06.
- Portée : Arch Linux, Ryoku, Niri, portable Dell.
- Environnements testés : Arch Linux x86_64, Niri 26.04, noyau 7.2.14 ; capteurs IIO visibles et rotation automatique confirmée par l’utilisateur.
- Prérequis et exclusions : le paquet système `iio-sensor-proxy` doit être installé ; le programme `iio-niri` 2.3.1 est installé dans `~/.local/bin`. Cette fiche ne configure pas l’affichage simultané de plusieurs workspaces.

## But ou problème

Faire pivoter automatiquement l’écran interne en fonction de l’accéléromètre, tout en gardant la gestion des fenêtres de Niri. L’écran interne est nommé `eDP-1`.

## Diagnostic

Le noyau expose deux accéléromètres IIO (`accel_3d`) et un capteur `dev_rotation`. Le paquet `iio-sensor-proxy` n’était pas installé lors de la préparation. Niri sait appliquer les transformations d’écran, et `iio-niri` relie les événements de `iio-sensor-proxy` à Niri.

La configuration Niri démarre `iio-niri` au lancement de la session seulement si `monitor-sensor` est disponible. Ainsi, sans le paquet système, le démarrage reste sans effet. La correspondance d’orientation par défaut de `iio-niri` est utilisée ; la rotation fonctionne sur ce portable.

## Procédure ou utilisation

### Activer la lecture du capteur

Dans un terminal Arch, installer le paquet système :

```sh
sudo pacman -S --needed iio-sensor-proxy
```

Lancer `monitor-sensor`, puis incliner l’écran pour vérifier que l’orientation change entre `normal`, `left-up`, `right-up` ou `bottom-up`. Terminer avec `Ctrl+C`.

### Démarrer la rotation dans Niri

La ligne de démarrage est dans `~/.config/niri/user.kdl` :

```kdl
spawn-sh-at-startup "command -v monitor-sensor >/dev/null 2>&1 && /home/remi/.local/bin/iio-niri listen --monitor eDP-1"
```

La prise en compte automatique se fait au prochain démarrage de Niri. L’état du service peut ensuite être lu avec :

```sh
iio-niri msg print-state
```

Le verrouillage est disponible pour une intégration ultérieure dans Control :

```sh
iio-niri msg toggle-lock-rotation
```

La commande bascule le verrouillage dans le processus `iio-niri` en cours.

### Disposition portrait des fenêtres

`~/.local/bin/niri-portrait-pairs` démarre avec Niri, écoute son flux IPC pour les changements de fenêtres/workspaces et vérifie la transformation de `eDP-1` chaque seconde. Quand l’écran passe en portrait, il regroupe deux colonnes voisines contenant chacune une seule fenêtre dans une colonne verticale pleine largeur. Les fenêtres supplémentaires forment les paires suivantes ; une dernière fenêtre isolée occupe une colonne pleine largeur. Les colonnes déjà empilées ne sont pas regroupées avec une autre.

Le compagnon garde en mémoire les largeurs du workspace en paysage et les rétablit à son retour. Si le workspace ne contient qu’une fenêtre en mosaïque, le compagnon ne la redimensionne pas : `always-center-single-column` et la largeur par défaut de Niri la gardent centrée. Les fenêtres flottantes ne sont pas modifiées. Le traitement s’applique au workspace actif de `eDP-1` lorsqu’il est activé ; il ne montre pas plusieurs workspaces en même temps.

Le compagnon utilise les actions natives `consume-window-into-column`, `expel-window-from-column` et `set-column-width` de Niri. Les paires qu’il a créées sont retirées au retour en paysage si elles sont encore dans la disposition attendue ; une modification manuelle de la pile est laissée en place.

### Comportement natif des fenêtres en portrait

Niri garde son défilement de colonnes horizontal après rotation de l’écran. Plusieurs fenêtres d’une même colonne sont empilées verticalement ; les raccourcis `Super+[` et `Super+]` configurés dans Ryoku permettent de consommer ou d’expulser une fenêtre vers la colonne voisine. `Super+Shift+R` fait défiler les hauteurs préréglées. Une seule colonne est centrée par la configuration actuelle.

Niri ne présente pas deux workspaces occupés simultanément en vue de travail normale. L’Overview les affiche en réduction. Cette fiche ne tente pas de créer ce comportement.

## Validation

- `niri validate --config ~/.config/niri/config.kdl` : configuration valide après ajout de `spawn-at-startup`.
- Compilation syntaxique de `niri-portrait-pairs` : réussie.
- Construction de `iio-niri` 2.3.1 depuis la référence Git `v2.3.1` (`8a3d9907063d724502cf95c210d681168b548361`) : réussie.
- Rotation physique avec `iio-sensor-proxy` et `iio-niri` : confirmée par l’utilisateur.
- Le compagnon tourne dans la session Niri actuelle et a mémorisé les largeurs du workspace actif en paysage.
- Aspect visuel des paires en portrait : confirmé par l’utilisateur.

## Persistance et maintenance

`~/.config/niri/user.kdl` est le fichier utilisateur de Niri sous Ryoku et n’est pas remplacé par ses mises à jour. `iio-niri` a été installé avec Cargo sous `~/.local/bin`; la mise à jour ou le retrait se gère avec Cargo. Le script `niri-portrait-pairs` est un script utilisateur Python sans dépendance externe ; son état de travail est gardé dans `$XDG_RUNTIME_DIR`.

## Sauvegarde et retour arrière

- Retirer les lignes `spawn-sh-at-startup` et `spawn-at-startup` de `~/.config/niri/user.kdl` pour désactiver respectivement la rotation et l’adaptation portrait.
- Retirer le binaire utilisateur avec `cargo uninstall iio-niri`.
- Ne retirer `iio-sensor-proxy` que s’il n’est plus utilisé par aucun autre logiciel.

## Références

- [Documentation Niri sur les sorties](https://niri-wm.github.io/niri/Configuration%3A-Outputs.html)
- [Projet iio-niri](https://github.com/Zhaith-Izaliel/iio-niri)
- [Paquet Arch Linux iio-sensor-proxy](https://archlinux.org/packages/extra/x86_64/iio-sensor-proxy/)
- [Documentation Niri sur les workspaces](https://niri-wm.github.io/niri/Workspaces.html)
