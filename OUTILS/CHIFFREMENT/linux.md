# Chiffrer et récupérer — Linux / Bash

Résumé : Commandes Bash pour chiffrer un fichier ou un dossier avec age et tar vers un objet à nom opaque, puis le déchiffrer en retrouvant les noms d'origine.

Ces commandes utilisent age, tar et OpenSSL. Lire [CHIFFREMENT.md](../../CHIFFREMENT.md) pour les clés, les noms opaques et les limites. Elles s’exécutent depuis la racine du dépôt ; adapter les chemins avant utilisation.

## Prérequis

Installer age avec le gestionnaire adapté : `sudo pacman -S age` sous Arch, `sudo apt install age` sous Debian/Ubuntu compatibles, ou `sudo dnf install age` sous Fedora. Les autres outils nécessaires sont `tar`, `openssl` et les utilitaires usuels. Vérifier `age --version` et `tar --version`.

## Chiffrer un fichier ou un dossier

Remplacer `/chemin/parent` et `source` par le parent et le nom du fichier ou dossier à protéger. Le dossier de sortie doit déjà exister. Pour une sauvegarde, choisir le `08-SAUVEGARDE/` de la portée concernée.

```bash
(
  set -euo pipefail
  umask 077
  destination="OS/Linux/arch/03-CONFIGURATION"
  objet="$(openssl rand -hex 16).age"
  temporaire="$(mktemp "$destination/.pending-XXXXXX")"
  trap 'rm -f -- "$temporaire"' EXIT

  tar -C /chemin/parent -czf - source |
    age -R .age-recipients -o "$temporaire"

  ln -- "$temporaire" "$destination/$objet"
  printf '%s\n' "$destination/$objet"
)
```

Le tar inclut les noms d’origine et les fichiers cachés présents sous `source`. Le flux est envoyé directement à age. Le nom final n’apparaît qu’après succès ; le lien final refuse de remplacer un objet existant. Le temporaire chiffré est supprimé à la sortie normale.

## Déchiffrer et retrouver les noms

Fournir un fichier d’identité privé externe et le chemin réel d’un objet opaque. Le dossier de travail créé est nouveau, privé et hors dépôt.

```bash
(
  set -euo pipefail
  umask 077
  travail="$(mktemp -d "${XDG_RUNTIME_DIR:-/tmp}/handbook-XXXXXX")"
  trap 'rm -f -- "$travail/archive.tar.gz"' EXIT

  age --decrypt --identity /chemin/prive/identite \
    --output "$travail/archive.tar.gz" \
    OS/Linux/arch/03-CONFIGURATION/IDENTIFIANT.age

  mkdir -- "$travail/contenu"
  tar -xkzf "$travail/archive.tar.gz" -C "$travail/contenu" \
    --no-same-owner --no-same-permissions
  printf 'Récupération locale : %s\n' "$travail/contenu"
)
```

Remplacer `IDENTIFIANT.age` par le vrai nom aléatoire. L’extraction est faite uniquement après succès du déchiffrement, sans mode verbeux. N’utiliser que les archives attendues et de confiance ; ne pas ajouter d’option tar `-P` qui autoriserait les chemins absolus. Les fichiers récupérés restent dans `contenu/` pour vérification et application manuelle.

Un adaptateur local facultatif peut fournir l’identité par un tube dédié à `age --decrypt --identity -`. Il ne doit jamais afficher la clé dans les échanges ou journaux ; son accès privé n’est pas documenté dans le dépôt. Les commandes ci-dessus fonctionnent sans adaptateur.
