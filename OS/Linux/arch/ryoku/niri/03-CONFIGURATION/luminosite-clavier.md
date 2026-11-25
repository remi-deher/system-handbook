# Luminosité minimale et pas des touches sous Niri

Résumé : une surcharge personnelle des touches de luminosité impose un minimum de 1 % sur l'écran intégré et des pas fins sous 5 %, avec retour possible aux raccourcis Ryoku.

- Statut : testé sur écran intégré ; touches et écran externe à vérifier selon le matériel.
- Date : 2026-11-13.
- Dernière vérification : 2026-11-25 ; noyau 7.3.4-arch1-2, Niri 26.04-1, Ryoku 1:1.1.0.r6233.g0bf1174-1 ; présence du script, syntaxe Bash et configuration Niri vérifiées, luminosité non modifiée lors de ce contrôle.
- Portée : Arch Linux, Ryoku, Niri ; shell Bash.
- Environnement testé : écran intégré de portable, Niri 26.04 ; essais matériels des paliers le 2026-11-13, sans validation des écrans externes.

## But et comportement

Les touches de luminosité pouvaient réduire le rétroéclairage sous 1 %. Le [script personnel](brightness-min.sh), adapté d'une commande Ryoku, arrondit le minimum au niveau matériel supérieur et sérialise les appuis. Sur l'écran intégré, la descente passe notamment par 10 → 5 → 4 → 1 %, et la remontée par 1 → 2 → 4 → 5 → 10 → 15 %. L'arrondi dépend de la résolution matérielle. Les écrans externes utilisent DDC/CI lorsque disponibles ; leur chemin conserve les pas demandés, sans ce minimum spécifique.

## Installation

Depuis ce dossier du dépôt, sous Bash, vérifier les chemins avec `ryoku owner` et préserver tout fichier existant avant de copier :

```bash
install -Dm755 brightness-min.sh "$HOME/.local/bin/ryoku-brightness-min"
```

Dans `~/.config/niri/user.kdl`, ajouter dans le bloc `binds` existant les deux lignes ci-dessous, en remplaçant `CHEMIN_ABSOLU` par le chemin du script installé. Éviter les doublons de raccourcis. Niri ne développe pas `$HOME` dans cet argument.

```kdl
XF86MonBrightnessUp allow-when-locked=true { spawn "CHEMIN_ABSOLU" "+5"; }
XF86MonBrightnessDown allow-when-locked=true { spawn "CHEMIN_ABSOLU" "-5"; }
```

Vérifier `niri validate -c ~/.config/niri/config.kdl`, puis essayer les touches en conservant un moyen de restaurer la luminosité. Niri recharge automatiquement une configuration valide. Le script utilise notamment `brightnessctl`, `flock` et `ryoku-hw-backlight` ; `ddcutil` est facultatif pour les écrans externes.

## Validation et maintenance

Les paliers et le plancher de l'écran intégré ont été essayés le 13 novembre, puis le niveau initial restauré. Le 25 novembre, seule la syntaxe du script et de la configuration a été vérifiée. Le script est une copie personnelle : il ne reçoit pas automatiquement les futures corrections de la commande Ryoku. Vérifier ses dépendances et son comportement après mise à jour.

## Retour arrière

Retirer seulement les deux raccourcis ajoutés dans `user.kdl`, valider la configuration et vérifier le retour des raccourcis Ryoku. Supprimer le script personnel uniquement après avoir vérifié qu'aucune autre configuration ne l'utilise. Restaurer une éventuelle copie précédente si elle existait.
