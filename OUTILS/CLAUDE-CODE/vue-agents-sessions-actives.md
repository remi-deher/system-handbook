# Vue agents de Claude Code : sessions actives seulement

- Résumé : la vue agents (`claude agents`, flèche gauche) et `claude agents --json` listent les sessions actives, pas l'historique ; les sessions terminées se reprennent par `/resume` ou `claude --resume <IDENTIFIANT>`, et une session créée depuis claude.ai n'y est pas toujours visible.
- Statut : testé partiellement (commandes lancées sur un poste réel ; l'affichage de la vue a été relevé par l'utilisateur, pas par l'assistant).
- Date : 2026-11-06.
- Portée : outil commun, Claude Code CLI, tous systèmes (le comportement ne dépend pas de l'OS).
- Environnements testés : Claude Code 2.1.318 sous Arch Linux. Windows et macOS : non testés.
- Prérequis et exclusions : Claude Code connecté. Ne couvre pas la configuration du service systemd, voir la [fiche Arch](../../OS/Linux/arch/04-LOGICIEL/claude-code/02-SYSTEME/service-systemd-remote-control.md).

## But ou problème

Après l'apparition de la vue agents et de Remote Control, des conversations locales semblent « disparaître » au lancement de `claude` et obligent à passer par `/resume`. Cette fiche dit ce que la vue montre vraiment et comment retrouver le reste.

## Diagnostic

- `claude agents --json` affiche les sessions actives (interactives et de fond) ; `--all` ajoute les sessions de fond terminées. Une session ordinaire du terminal, une fois fermée, n'y figure plus. Constaté : 4 sessions listées, toutes en cours.
- Cette version contient les réglages `defaultToAgentsView` et `leftArrowOpensAgents` (fichier global de configuration de l'utilisateur) et `disableAgentView` (réglage de `settings.json`, ou variable `CLAUDE_CODE_DISABLE_AGENT_VIEW=1`). `defaultToAgentsView` est une clé de la configuration globale de l'application, pas de `settings.json`.
- Écart observé : une session créée depuis claude.ai et exécutée par le service (statut `idle`) apparaissait dans `claude agents --json --all` alors que l'écran de la vue ne la montrait pas. Cause non trouvée : filtre sur le statut `idle`, sur les sessions pilotées à distance, ou autre.
- Les sessions de fond vides créées par `claude --bg` apparaissent comme « new session » dans la vue.
- `claude --bg --resume <IDENTIFIANT>` reprend la session sous le même identifiant si aucun processus ne la tient ; sinon Claude crée une copie sous un autre identifiant et le dit : `note: session … is open in another Claude Code process, so this started a copy`.
- `claude attach <ID_COURT>` ouvre une session de fond dans le terminal ; `claude stop <ID_COURT>` l'arrête en conservant la conversation ; `claude rm <ID_COURT>` la supprime.
- Un réglage de configuration globale peut être réécrit par une session déjà ouverte : après un changement, relire la valeur au bout de quelques instants.

## Procédure ou utilisation

Lister ce que voit la vue (bash) :

```bash
claude agents --json            # sessions actives
claude agents --json --all      # y compris les sessions de fond terminées
```

Retrouver une conversation terminée :

1. `/resume` pour les sessions du terminal ; la reprise par identifiant reste possible pour toutes :

   ```bash
   claude --resume <IDENTIFIANT>
   ```

2. Pour la voir ensuite dans la vue agents : `claude --bg --resume <IDENTIFIANT>`, puis `claude attach <ID_COURT>`.
3. Pour les sessions créées depuis claude.ai, voir [Sessions Remote Control absentes de `/resume`](sessions-masquees-resume.md).

Nettoyer les sessions de fond de test : `claude stop <ID_COURT>`, puis `claude rm <ID_COURT>`.

## Validation

Essais réels (Claude Code 2.1.318, Linux) : sortie JSON relevée par l'assistant ; reprise `--bg --resume` et `attach` confirmées par l'utilisateur ; affichage de la vue relevé par l'utilisateur sur capture d'écran. Non vérifié : le comportement exact de `defaultToAgentsView` au lancement et la raison de l'écart entre la sortie JSON et l'écran.

## Persistance et maintenance

Comportement susceptible de changer à chaque version de Claude Code : revérifier après une mise à jour.

## Références

- [Sessions Remote Control absentes de `/resume`](sessions-masquees-resume.md).
- [Service systemd Remote Control sous Arch](../../OS/Linux/arch/04-LOGICIEL/claude-code/02-SYSTEME/service-systemd-remote-control.md), dont la section « Limites constatées » décrit la reprise locale d'une session web.
