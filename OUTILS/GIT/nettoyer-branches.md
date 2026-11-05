# Nettoyer les branches locales validées

Résumé : script bash qui supprime les branches locales (et leurs worktrees) dont les commits sont déjà dans une pull request fusionnée ou dans la branche par défaut, en conservant tout ce qui n'est pas publié.

- Statut : testé (dépôt jetable avec worktree ; simulation sur ce dépôt). La suppression réelle n'a pas été lancée sur le dépôt de travail.
- Date : 2026-11-05.
- Portée : outil commun, Linux, bash.
- Environnements testés : Arch Linux, Git et `gh` récents ; aucun autre système.
- Prérequis et exclusions : `git`, et `gh` connecté pour reconnaître les fusions « squash ». Sans `gh`, seules les branches contenues dans la branche par défaut sont reconnues.

## But ou problème

Le dépôt supprime déjà les branches distantes une fois la PR fusionnée ([auto-merge.yml](../../.github/workflows/auto-merge.yml) et un filet de sécurité nocturne). Restent les branches locales, les références distantes obsolètes et les worktrees, qui s'accumulent.

Git ne sait pas qu'une branche fusionnée en « squash » est terminée : `git branch -d` la refuse. Le script compare donc la pointe locale à la tête de la PR fusionnée.

## Procédure ou utilisation

Script : [nettoyer-branches.sh](nettoyer-branches.sh), à lancer depuis le dépôt (bash).

```bash
bash OUTILS/GIT/nettoyer-branches.sh            # simulation, ne supprime rien
bash OUTILS/GIT/nettoyer-branches.sh --apply    # supprime après avoir relu la simulation
```

Options : `--no-fetch` (pas de `git fetch --prune` préalable), `--remote NOM` (remote autre que `origin`).

Une branche est supprimée seulement si sa pointe est contenue dans la tête d'une PR fusionnée ou dans la branche par défaut distante. Elle est conservée dans tous les autres cas :

- des commits locaux absents de toute PR fusionnée (par exemple des notes ajoutées après la fusion) ;
- aucune PR, ou une PR encore ouverte ;
- la branche est extraite dans le dépôt principal ;
- le worktree associé contient des modifications non commitées.

Le script supprime aussi le worktree d'une branche supprimée, puis lance `git worktree prune`.

### Automatiser la mise à jour des références

Pour que les références distantes disparues soient retirées à chaque `git fetch` :

```bash
git config --global fetch.prune true
```

## Validation

- Essai réel dans un dépôt jetable : la branche fusionnée et son worktree sont supprimés, la branche avec un commit non fusionné est conservée.
- Simulation sur ce dépôt : les branches de PR fusionnées sont repérées, celles qui portent des commits locaux sont conservées.
- Non testé : dépôt sans `gh`, dépôt avec plusieurs remotes.

## Persistance et maintenance

Le script n'est ni planifié ni installé automatiquement. Le lancer à la main après une série de fusions.

## Sauvegarde et retour arrière

Une branche supprimée se retrouve avec `git reflog` (pointe locale) tant que Git n'a pas fait le ménage. Pour garder une copie, pousser la branche avant de lancer `--apply`.

## Références

- [auto-merge.yml](../../.github/workflows/auto-merge.yml) : nettoyage côté GitHub.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) : flux de contribution par pull request.
