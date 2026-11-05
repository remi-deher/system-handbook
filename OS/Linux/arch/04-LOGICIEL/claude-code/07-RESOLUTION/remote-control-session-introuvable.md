# Remote Control : session introuvable, sans réponse ou service bloqué

- Résumé : liste des pièges rencontrés avec `claude remote-control` en service (session absente de l'application ou de `/resume`, message sans réponse, erreur « already served », service actif mais mort) et leur cause.
- Statut : résolu en partie (confirmé par l'utilisateur) ; certaines causes restent des hypothèses signalées comme telles. Le service a finalement été désactivé le 2026-11-06, voir la fiche de fonctionnement.
- Date : 2026-11-06.
- Portée : Claude Code CLI sur Linux avec le service de la fiche [service systemd Remote Control](../02-SYSTEME/service-systemd-remote-control.md).
- Environnements testés : Claude Code 2.1.318 sous Arch Linux.
- Prérequis et exclusions : service installé et connecté ; ne couvre pas les problèmes d'authentification Claude.

## But ou problème

Symptômes : la session créée depuis le téléphone n'apparaît pas, ou apparaît sans réponse de la machine ; une session créée depuis claude.ai dans l'environnement du service n'apparaît ni dans `/resume` ni dans le tableau de bord du terminal ; le service reste « actif » sans rien faire ; le journal affiche `Error: This folder is already served by a terminal claude remote-control on this device`.

## Diagnostic

- **Session sans réponse** : le plus souvent le lien ou la liste de l'application vise un ancien environnement. Chaque démarrage sans fichier `bridge-pointer.json` crée un environnement neuf et supprime l'ancien. Vérifier l'identifiant d'environnement dans `journalctl --user -u claude-remote-control` et rouvrir la liste de l'application.
- **Service actif mais mort** : le lanceur gardait un `sleep infinity` en vie après la mort de `claude`. Utiliser le lanceur `bash` de la fiche de fonctionnement avec `Restart=always`.
- **« already served »** : se produit juste après l'arrêt d'une instance (verrou pas encore libéré) ou après un essai avec `--continue` qui laisse l'environnement enregistré. Le service se relance seul et passe au bout de quelques minutes. Hypothèse non vérifiée : l'option « Remote Control pour toutes les sessions » peut aggraver ce cas.
- **Session fantôme qui échoue au démarrage** : `bridge-pointer.json` pointait vers une session supprimée côté Claude. Remplacer son champ `sessionId` par celui d'une session existante, service arrêté, en gardant `environmentId` ; sauvegarder le fichier avant.
- **`--continue` inutilisable ici** : incompatible avec `--no-create-session-in-dir`, et il se rattache à la dernière session enregistrée (supprimée dans notre cas), qui échoue.
- **Anciennes sessions** : un arrêt du service archive ses sessions ; les désarchiver dans l'application et leur envoyer un message pour qu'elles reviennent.
- **Session créée depuis claude.ai ou le téléphone absente de `/resume` et du tableau de bord** : elle est bien enregistrée sur la machine mais Claude Code la masque du sélecteur ; ce n'est pas propre à Linux. Voir [Sessions Remote Control absentes de `/resume`](../../../../../../OUTILS/CLAUDE-CODE/sessions-masquees-resume.md) pour la cause et la reprise par identifiant.
- **Conversations « perdues » alors que les transcripts existent** : vérifier d'abord `ls ~/.claude/projects/<dossier>/*.jsonl`. Dans nos essais, aucun transcript n'avait disparu : les conversations étaient masquées de `/resume` (sessions du service) ou archivées côté Claude après un redémarrage du service (voir la fiche de fonctionnement, « Limites constatées »).
- **Conversation web « Remote Control déconnecté »** : le processus `claude --print --sdk-url …` qui la servait a été terminé. La reprise locale (`claude --bg --resume <IDENTIFIANT>`, `claude attach <ID_COURT>`) fonctionne mais ne la rattache pas ; activer Remote Control sur la session reprise crée une nouvelle conversation web liée au même transcript.
- **Message envoyé depuis la CLI absent de claude.ai** : la session locale reprise n'est reliée à aucune conversation web tant que Remote Control n'y est pas activé.
- **Vue agents (`claude agents`, flèche gauche)** : elle liste les sessions actives, pas l'historique ; voir [la fiche outils](../../../../../../OUTILS/CLAUDE-CODE/vue-agents-sessions-actives.md).

Pour voir ce que le serveur reçoit, ajouter temporairement `--debug-file <chemin>` à la commande : le journal contient le contenu des conversations. Le supprimer ensuite.

## Procédure ou utilisation

1. Lire l'état : `systemctl --user status claude-remote-control` et `journalctl --user -fu claude-remote-control`.
2. Noter l'identifiant d'environnement affiché et rouvrir celui-là dans l'application.
3. Éviter de redémarrer le service pendant un test : chaque redémarrage peut changer l'état côté application.

## Validation

Essais réels : message du téléphone reçu et traité, session reprise après redémarrage du service. Reprise après redémarrage de la machine non testée.

## Sauvegarde et retour arrière

Copie de `~/.claude/projects/<dossier>/bridge-pointer.json` avant toute modification.
