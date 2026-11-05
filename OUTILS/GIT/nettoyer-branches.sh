#!/usr/bin/env bash
# Nettoie les branches locales (et les worktrees associés) déjà validées et poussées.
#
# Une branche locale est supprimable seulement si sa pointe est sûre :
#   - la pointe est contenue dans la tête d'une pull request fusionnée (« gh »), ou
#   - la branche est entièrement contenue dans la branche par défaut distante.
# Une branche avec des commits absents de la PR fusionnée, une PR ouverte, ou sans PR, est conservée.
# Par défaut : simulation. Rien n'est supprimé sans --apply.
#
# Usage : nettoyer-branches.sh [--apply] [--no-fetch] [--remote NOM]
set -euo pipefail

APPLY=0; FETCH=1; REMOTE=origin
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --no-fetch) FETCH=0; shift ;;
    --remote) REMOTE="${2:?--remote demande une valeur}"; shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Option inconnue : $1" >&2; exit 2 ;;
  esac
done

git rev-parse --git-dir >/dev/null 2>&1 || { echo "Pas dans un dépôt Git." >&2; exit 1; }
HAS_GH=0; command -v gh >/dev/null && HAS_GH=1
[ "$HAS_GH" = 1 ] || echo "gh absent : seules les branches contenues dans la branche par défaut seront reconnues." >&2

[ "$FETCH" = 1 ] && git fetch --prune --quiet "$REMOTE"

DEFAULT="$(git symbolic-ref --quiet --short "refs/remotes/$REMOTE/HEAD" 2>/dev/null || true)"
[ -n "$DEFAULT" ] || { echo "Branche par défaut de $REMOTE inconnue (git remote set-head $REMOTE -a)." >&2; exit 1; }
DEFAULT_LOCAL="${DEFAULT#"$REMOTE"/}"

# Branche -> dossier du worktree qui l'a extraite (le premier worktree est le dépôt principal).
declare -A WT_OF; MAIN_WT=""
wt=""
while IFS= read -r line; do
  case "$line" in
    "worktree "*) wt="${line#worktree }"; [ -n "$MAIN_WT" ] || MAIN_WT="$wt" ;;
    "branch "*) WT_OF["${line#branch refs/heads/}"]="$wt" ;;
  esac
done < <(git worktree list --porcelain)

DELETED=0; KEPT=0
for branch in $(git for-each-ref --format='%(refname:short)' refs/heads); do
  [ "$branch" != "$DEFAULT_LOCAL" ] || continue
  tip="$(git rev-parse "refs/heads/$branch")"
  reason=""

  if [ "$HAS_GH" = 1 ]; then
    # Une PR fusionnée dont la tête contient la pointe locale : aucun commit local n'est perdu.
    while read -r num oid; do
      [ -n "$num" ] || continue
      git cat-file -e "$oid^{commit}" 2>/dev/null || git fetch --quiet "$REMOTE" "pull/$num/head" 2>/dev/null || true
      if git merge-base --is-ancestor "$tip" "$oid" 2>/dev/null; then reason="contenue dans la PR #$num fusionnée"; break; fi
    done < <(gh pr list --head "$branch" --state merged --json number,headRefOid --jq '.[] | "\(.number) \(.headRefOid)"' 2>/dev/null)
  fi
  if [ -n "$reason" ]; then
    :
  elif git merge-base --is-ancestor "$tip" "$DEFAULT" 2>/dev/null; then
    reason="contenue dans $DEFAULT"
  fi

  if [ -z "$reason" ]; then
    echo "garde      $branch (commits absents de toute PR fusionnée, ou pas de PR)"; KEPT=$((KEPT+1)); continue
  fi

  dir="${WT_OF[$branch]:-}"
  if [ -n "$dir" ] && [ "$dir" = "$MAIN_WT" ]; then
    echo "garde      $branch (extraite dans le dépôt principal, à changer de branche d'abord)"; KEPT=$((KEPT+1)); continue
  fi
  if [ -n "$dir" ] && [ -n "$(git -C "$dir" status --porcelain)" ]; then
    echo "garde      $branch (worktree $dir avec des modifications non commitées)"; KEPT=$((KEPT+1)); continue
  fi

  if [ "$APPLY" = 1 ]; then
    [ -z "$dir" ] || git worktree remove "$dir"
    git branch -D "$branch" >/dev/null
    echo "supprimée  $branch ($reason)"
  else
    echo "supprimerait $branch ($reason)${dir:+ + worktree $dir}"
  fi
  DELETED=$((DELETED+1))
done

git worktree prune
[ "$APPLY" = 1 ] || echo "Simulation : relancer avec --apply pour supprimer."
echo "$DELETED à supprimer/supprimée(s), $KEPT conservée(s)."
