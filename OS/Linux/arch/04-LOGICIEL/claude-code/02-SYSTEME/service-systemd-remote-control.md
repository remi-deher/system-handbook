# Claude Code en service systemd avec Remote Control

- Résumé : un service systemd utilisateur lance `claude remote-control` au démarrage, ce qui garde une session Claude Code accessible depuis le téléphone ou claude.ai/code et la reprend après un redémarrage du service.
- Statut : testé (confirmé par l'utilisateur : session visible et synchronisée des deux côtés, reprise après redémarrage du service).
- Date : 2026-11-05.
- Portée : Arch Linux, Claude Code (CLI), systemd en mode utilisateur.
- Environnements testés : Arch Linux, Claude Code 2.1.318, systemd utilisateur avec linger activé, shell de connexion fish (le service lance bash). Redémarrage du service testé ; redémarrage complet de la machine non testé.
- Prérequis et exclusions : compte Claude avec abonnement, `claude` connecté (`claude` lancé au moins une fois), dossier de travail approuvé. Remote Control est décrit dans la [documentation officielle](https://code.claude.com/docs/fr/remote-control) ; son comportement peut changer d'une version à l'autre.

## But ou problème

Garder en permanence, en arrière-plan, un Claude Code piloté à distance : on ouvre ou reprend une session depuis le téléphone (application Claude) ou un navigateur, et Claude travaille sur la machine. Sans service, il faut garder un terminal ouvert avec `claude remote-control`.

## Diagnostic

Constats vérifiés pendant la mise en place :

- `claude remote-control` pose une question de confirmation (« Enable Remote Control? (y/n) ») et quitte quand il n'a pas de terminal. Il faut donc répondre `y` par l'entrée standard.
- Si l'entrée standard est fermée juste après le `y`, le programme peut s'arrêter ; on la garde ouverte avec `sleep infinity`.
- Avec `exec` ou un `sh -c` qui attend `sleep`, le service reste « actif » même quand `claude` est mort et systemd ne le relance jamais. Le lanceur doit être un `bash` (sans `exec` sur `claude`) qui se termine avec `claude`, avec `Restart=always`.
- Chaque démarrage enregistre un environnement côté Claude. L'identifiant de cet environnement et de la dernière session est mémorisé dans `~/.claude/projects/<dossier-de-travail>/bridge-pointer.json` : tant que ce fichier existe, le serveur retrouve le même environnement et reprend la dernière session. L'option `--no-create-session-in-dir` désactivait ce comportement (environnement neuf à chaque démarrage) et a été retirée.
- Un arrêt du service archive ses sessions côté Claude. Au redémarrage, seule la dernière session enregistrée revient ; les plus anciennes se retrouvent en les désarchivant dans l'application puis en leur envoyant un message.

## Procédure ou utilisation

1. Installer le service avec le script [setup-claude-remote-control.sh](../05-SCRIPT/setup-claude-remote-control.md) (idempotent) :

   ```bash
   bash setup-claude-remote-control.sh            # nom de session = nom de la machine
   bash setup-claude-remote-control.sh --name MON_NOM
   ```

2. Le script crée `~/.config/systemd/user/claude-remote-control.service` et `~/.config/claude-remote-control.env`, active le linger, puis active et démarre le service.
3. Dans l'application Claude (onglet Code) ou sur claude.ai/code, choisir l'environnement portant le nom de la machine et créer une session.

Commandes utiles (bash) :

```bash
systemctl --user status claude-remote-control
journalctl --user -fu claude-remote-control
systemctl --user restart claude-remote-control
```

### Remote Control activé pour toutes les sessions

Dans `/config` de Claude Code, l'option « Enable Remote Control for all sessions » (clé `remoteControlAtStartup` de `~/.claude/settings.json`) a aussi été activée, selon [la documentation](https://code.claude.com/docs/fr/remote-control#enable-remote-control-for-all-sessions). Chaque session Claude Code ouverte localement s'enregistre alors aussi auprès de Remote Control. L'effet exact combiné au service n'a pas été mesuré : le service fonctionne avec cette option, mais les sessions locales peuvent apparaître dans la liste de l'application à côté de celles du service, et une erreur « This folder is already served » au démarrage du service doit faire suspecter cette option.

## Validation

- Essai réel : un message envoyé depuis le téléphone atteint la machine, Claude répond et la conversation est synchronisée des deux côtés.
- Essai réel : après `systemctl --user restart`, l'environnement reste le même et la dernière session est reprise.
- Non testé : redémarrage complet de la machine et reprise après plus de quatre heures d'arrêt (la documentation parle d'environ quatre heures pour la restauration des sessions).

## Persistance et maintenance

- Le service démarre avec la session utilisateur grâce au linger (`loginctl enable-linger`) et à `WantedBy=default.target`.
- Une mise à jour de Claude Code remplace le binaire sans toucher au service ; le `PATH` du service inclut `~/.local/bin`. Si `claude` est installé ailleurs, ajouter son dossier à la ligne `Environment=PATH=` du script.
- Ne pas supprimer `bridge-pointer.json` : l'environnement changerait et les liens ou QR mémorisés deviendraient périmés.

## Sauvegarde et retour arrière

- Retour arrière : `systemctl --user disable --now claude-remote-control`, puis supprimer l'unité et `claude-remote-control.env` dans `~/.config`.
- Résolution des problèmes : [session introuvable ou sans réponse](../07-RESOLUTION/remote-control-session-introuvable.md).

## Références

- [Documentation Remote Control](https://code.claude.com/docs/fr/remote-control)
- [Option d'activation pour toutes les sessions](https://code.claude.com/docs/fr/remote-control#enable-remote-control-for-all-sessions)
