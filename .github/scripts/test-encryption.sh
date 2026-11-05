#!/usr/bin/env bash
# Aller-retour de chiffrement age + tar (commandes de OUTILS/CHIFFREMENT/linux.md)
# avec des données fictives et une clé jetable. N'utilise ni le dépôt ni de secret.
set -euo pipefail

work="$(mktemp -d)"
trap 'rm -rf -- "$work"' EXIT
cd "$work"

fail() { printf 'ÉCHEC : %s\n' "$1" >&2; exit 1; }

# Clé jetable, créée et détruite dans ce test.
age-keygen -o identite.txt 2>/dev/null
age-keygen -y identite.txt > .age-recipients
age-keygen -o autre-identite.txt 2>/dev/null

# Données fictives : noms Unicode, fichier caché, dossier vide, sous-dossier.
mkdir -p dest parent/source/dossier-vide "parent/source/répertoire é ü/sous dossier"
printf 'contenu fictif\n' > "parent/source/note é ü 日本.txt"
printf 'caché\n' > parent/source/.cache
printf 'profond\n' > "parent/source/répertoire é ü/sous dossier/fichier.txt"

# Chiffrement (bloc « Chiffrer un fichier ou un dossier »).
sortie="$(
  set -euo pipefail
  umask 077
  destination="dest"
  objet="$(openssl rand -hex 16).age"
  temporaire="$(mktemp "$destination/.pending-XXXXXX")"
  trap 'rm -f -- "$temporaire"' EXIT

  tar -C "$work/parent" -czf - source |
    age -R .age-recipients -o "$temporaire"

  ln -- "$temporaire" "$destination/$objet"
  printf '%s\n' "$destination/$objet"
)"

[[ "$sortie" =~ ^dest/[0-9a-f]{32}\.age$ ]] || fail "nom d'objet non opaque : $sortie"
head -c 21 "$sortie" | grep -q '^age-encryption.org/v1' || fail "en-tête age absent"
compgen -G 'dest/.pending-*' >/dev/null && fail "temporaire non supprimé"
if grep -aq 'note' "$sortie" || grep -aq 'fictif' "$sortie"; then fail "contenu ou nom en clair"; fi

# Déchiffrement (bloc « Déchiffrer et retrouver les noms »).
resultat="$(
  set -euo pipefail
  umask 077
  travail="$(mktemp -d "${XDG_RUNTIME_DIR:-/tmp}/handbook-XXXXXX")"
  trap 'rm -f -- "$travail/archive.tar.gz"' EXIT

  age --decrypt --identity identite.txt \
    --output "$travail/archive.tar.gz" \
    "$sortie"

  mkdir -- "$travail/contenu"
  tar -xkzf "$travail/archive.tar.gz" -C "$travail/contenu" \
    --no-same-owner --no-same-permissions
  printf 'Récupération locale : %s\n' "$travail/contenu"
)"
recupere="${resultat#Récupération locale : }"
trap 'rm -rf -- "$work" "$(dirname -- "$recupere")"' EXIT

diff -r parent/source "$recupere/source" || fail "contenu récupéré différent de l'original"
[ -f "$recupere/source/.cache" ] || fail "fichier caché perdu"
[ -d "$recupere/source/dossier-vide" ] || fail "dossier vide perdu"

# Un mauvais jeton d'identité ne doit rien déchiffrer.
if age --decrypt --identity autre-identite.txt --output mauvais.tar.gz "$sortie" 2>/dev/null; then
  fail "déchiffrement accepté avec une autre identité"
fi
[ ! -s mauvais.tar.gz ] || fail "sortie produite malgré l'échec"

# Le lien final ne doit pas remplacer un objet existant.
if ln -- "$sortie" "$sortie" 2>/dev/null; then fail "écrasement d'un objet existant"; fi

printf 'Aller-retour Linux valide.\n'
