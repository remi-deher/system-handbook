# Sessions Remote Control absentes de /resume et du tableau de bord

- Résumé : les sessions créées depuis claude.ai ou le téléphone dans un environnement Remote Control sont enregistrées sur la machine mais masquées de `/resume` et du tableau de bord ; on les reprend avec `claude --resume <IDENTIFIANT>`.
- Statut : testé sous Linux (reprise par identifiant confirmée par l'utilisateur) ; la cause est déduite, pas lue à l'endroit de l'appel.
- Date : 2026-11-05.
- Portée : outil commun, Claude Code CLI, tous systèmes (le comportement ne dépend pas de l'OS).
- Environnements testés : Claude Code 2.1.318 sous Arch Linux. Windows et macOS : non testés.
- Prérequis et exclusions : environnement lancé avec `claude remote-control`. Ne couvre pas le service systemd, voir la [fiche Arch](../../OS/Linux/arch/04-LOGICIEL/claude-code/07-RESOLUTION/remote-control-session-introuvable.md).

## But ou problème

Une session créée depuis claude.ai ou l'application mobile, dans son propre environnement Remote Control, n'apparaît ni dans `/resume` ni dans le tableau de bord du terminal. Les sessions ouvertes dans le terminal, elles, apparaissent.

## Diagnostic

- La conversation est bien enregistrée : le fichier `<IDENTIFIANT>.jsonl` existe dans le dossier des projets de Claude Code (`~/.claude/projects/<dossier>/` sous Linux) et contient tous les messages.
- Ces sessions sont lancées avec `entrypoint` valant `sdk-cli` et `promptSource` valant `sdk` ; une session du terminal a `entrypoint` valant `cli`.
- Dans le binaire 2.1.318, une fonction exportée sous le nom `isHiddenFromSessionPicker` renvoie « vrai » pour les `entrypoint` `sdk-cli`, `sdk-ts` et `sdk-py` et pour les `sessionKind` `daemon` et `daemon-worker`.
- Hypothèse non vérifiée de bout en bout : l'endroit où `/resume` et le tableau de bord appellent ce filtre est dans du code compilé en bytecode, illisible. La cause est déduite du nom, du contenu de la fonction et des essais.
- Les identifiants de ces sessions sont des UUID de version 5 (le troisième groupe commence par `5`), ceux du terminal des UUID de version 4. Cela permet de les repérer.

Ce n'est ni une perte de sauvegarde, ni un défaut de configuration. Aucun réglage pour afficher ces sessions n'a été trouvé.

## Procédure ou utilisation

1. Lister les dernières sessions créées à distance (bash, Linux) :

   ```bash
   ls -t ~/.claude/projects/*/*-5???-*.jsonl | head -5
   ```

   Sous Windows, le dossier est `%USERPROFILE%\.claude\projects\` (non testé).

2. Reprendre une session par son identifiant, c'est-à-dire le nom du fichier sans `.jsonl` :

   ```bash
   claude --resume <IDENTIFIANT>
   ```

La reprise par identifiant ne passe pas par le sélecteur, donc le filtre ne s'applique pas.

## Validation

Essai réel (Claude Code 2.1.318, Linux) : une session créée depuis claude.ai est absente de `/resume` et du tableau de bord, mais `claude --resume <IDENTIFIANT>` l'ouvre avec sa conversation. Le test sous Windows et macOS n'a pas été fait.

## Persistance et maintenance

Une mise à jour de Claude Code peut changer ce filtre. Revérifier après chaque changement de version majeure.

## Références

- [Remote Control : session introuvable, sans réponse ou service bloqué](../../OS/Linux/arch/04-LOGICIEL/claude-code/07-RESOLUTION/remote-control-session-introuvable.md) pour les problèmes propres au service Linux.
