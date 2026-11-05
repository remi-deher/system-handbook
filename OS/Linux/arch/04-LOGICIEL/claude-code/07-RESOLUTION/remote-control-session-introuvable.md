# Remote Control : session introuvable, sans réponse ou service bloqué

- Résumé : liste des pièges rencontrés avec `claude remote-control` en service (session absente de l'application, message sans réponse, erreur « already served », service actif mais mort) et leur cause.
- Statut : résolu (confirmé par l'utilisateur) ; certaines causes restent des hypothèses signalées comme telles.
- Date : 2026-11-05.
- Portée : Claude Code CLI sur Linux avec le service de la fiche [service systemd Remote Control](../02-SYSTEME/service-systemd-remote-control.md).
- Environnements testés : Claude Code 2.1.318 sous Arch Linux.
- Prérequis et exclusions : service installé et connecté ; ne couvre pas les problèmes d'authentification Claude.

## But ou problème

Symptômes : la session créée depuis le téléphone n'apparaît pas, ou apparaît sans réponse de la machine ; le service reste « actif » sans rien faire ; le journal affiche `Error: This folder is already served by a terminal claude remote-control on this device`.

## Diagnostic

- **Session sans réponse** : le plus souvent le lien ou la liste de l'application vise un ancien environnement. Chaque démarrage sans fichier `bridge-pointer.json` crée un environnement neuf et supprime l'ancien. Vérifier l'identifiant d'environnement dans `journalctl --user -u claude-remote-control` et rouvrir la liste de l'application.
- **Service actif mais mort** : le lanceur gardait un `sleep infinity` en vie après la mort de `claude`. Utiliser le lanceur `bash` de la fiche de fonctionnement avec `Restart=always`.
- **« already served »** : se produit juste après l'arrêt d'une instance (verrou pas encore libéré) ou après un essai avec `--continue` qui laisse l'environnement enregistré. Le service se relance seul et passe au bout de quelques minutes. Hypothèse non vérifiée : l'option « Remote Control pour toutes les sessions » peut aggraver ce cas.
- **Session fantôme qui échoue au démarrage** : `bridge-pointer.json` pointait vers une session supprimée côté Claude. Remplacer son champ `sessionId` par celui d'une session existante, service arrêté, en gardant `environmentId` ; sauvegarder le fichier avant.
- **`--continue` inutilisable ici** : incompatible avec `--no-create-session-in-dir`, et il se rattache à la dernière session enregistrée (supprimée dans notre cas), qui échoue.
- **Anciennes sessions** : un arrêt du service archive ses sessions ; les désarchiver dans l'application et leur envoyer un message pour qu'elles reviennent.

Pour voir ce que le serveur reçoit, ajouter temporairement `--debug-file <chemin>` à la commande : le journal contient le contenu des conversations. Le supprimer ensuite.

## Procédure ou utilisation

1. Lire l'état : `systemctl --user status claude-remote-control` et `journalctl --user -fu claude-remote-control`.
2. Noter l'identifiant d'environnement affiché et rouvrir celui-là dans l'application.
3. Éviter de redémarrer le service pendant un test : chaque redémarrage peut changer l'état côté application.

## Validation

Essais réels : message du téléphone reçu et traité, session reprise après redémarrage du service. Reprise après redémarrage de la machine non testée.

## Sauvegarde et retour arrière

Copie de `~/.claude/projects/<dossier>/bridge-pointer.json` avant toute modification.
