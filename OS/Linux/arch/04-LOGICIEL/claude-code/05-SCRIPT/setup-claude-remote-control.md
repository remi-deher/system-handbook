# setup-claude-remote-control : installer le service Remote Control

- Résumé : script bash idempotent qui crée et active le service systemd utilisateur `claude-remote-control` ; sans chemin ni nom de machine en dur.
- Statut : archivé, le service qu'il installe a été abandonné le 2026-11-06 (voir la [fiche de fonctionnement](../02-SYSTEME/service-systemd-remote-control.md)) ; script testé (exécuté plusieurs fois, relance sans effet de bord).
- Date : 2026-11-05.
- Dernière vérification : 2026-11-13, Claude Code 2.1.323 sous Arch Linux : le service `claude-remote-control` n'existe plus (`systemctl --user is-enabled claude-remote-control` répond `not-found`) ; les procédures n'ont pas été rejouées.
- Portée : Arch Linux et distributions avec systemd, Claude Code CLI.
- Environnements testés : Arch Linux, Claude Code 2.1.318, bash ; aucune autre distribution.
- Prérequis et exclusions : `claude` dans le `PATH`, `systemctl --user`, `loginctl`. Sans systemd, ne convient pas.

## But ou problème

Reproduire la même installation du service sur n'importe quelle machine ou pour n'importe quel utilisateur. Voir la fiche [service systemd Remote Control](../02-SYSTEME/service-systemd-remote-control.md) pour le fonctionnement.

## Procédure ou utilisation

Script : [setup-claude-remote-control.sh](setup-claude-remote-control.sh).

```bash
bash setup-claude-remote-control.sh              # nom de session = nom de la machine
bash setup-claude-remote-control.sh --name NOM   # nom fixé dans ~/.config/claude-remote-control.env
```

Le script :

- vérifie que `claude` est dans le `PATH` et avertit si le dossier personnel n'est pas approuvé (divergence constatée le 2026-11-13 : répondre « Yes » dans `~` ne semble pas persister, voir [la fiche de résolution](../07-RESOLUTION/confiance-dossier-personnel-redemandee.md)) ;
- écrit `~/.config/systemd/user/claude-remote-control.service` (avec `%h` et `%H`, donc aucun chemin ni nom en dur) et crée `~/.config/claude-remote-control.env` s'il n'existe pas ;
- répond `y` automatiquement à la question de confirmation de Remote Control ;
- active le linger si besoin, recharge systemd, active le service et ne le redémarre que si l'unité a changé ou s'il est arrêté.

## Validation

- Essai réel de deux exécutions successives : la seconde ne change rien ni ne redémarre le service.
- Un redémarrage du service change l'environnement seulement si le fichier mémorisant la session a disparu (voir la fiche de fonctionnement).

## Persistance et maintenance

Relancer le script après toute modification pour régénérer l'unité. Le fichier d'environnement n'est écrasé qu'avec `--name`.

## Sauvegarde et retour arrière

Voir la procédure de retour arrière de la fiche de fonctionnement.
