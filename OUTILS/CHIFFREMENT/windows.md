# Chiffrer et récupérer — Windows / PowerShell

Résumé : Commandes PowerShell 5.1 et 7 pour chiffrer et déchiffrer avec age.exe et tar.exe sous Windows natif, avec les limites observées (noms japonais, ordre des tar.exe).

Ces commandes visent Windows 10 récent ou Windows 11 avec Windows PowerShell 5.1 ou PowerShell 7, `age.exe` et `tar.exe`. Lire [CHIFFREMENT.md](../../CHIFFREMENT.md) pour les clés et les limites. Exécuter depuis la racine du dépôt et adapter les chemins.

## Prérequis

Installer age avec WinGet si disponible :

```powershell
winget install --id FiloSottile.age --exact
```

Rouvrir PowerShell après l’installation pour prendre en compte le chemin de l’exécutable, puis vérifier :

```powershell
age --version
Get-Command tar.exe
```

À défaut de WinGet, utiliser la distribution Windows officielle d’age. Saisir la phrase secrète à l’invite interactive.

Ne pas copier le pipeline binaire Bash dans Windows PowerShell 5.1 : sa conversion des sorties natives peut altérer les octets. Les exemples passent par un tar temporaire dans le répertoire temporaire du profil utilisateur, hors dépôt.

## Chiffrer un fichier ou dossier

Remplacer `C:\chemin\parent` et `source` par le parent et le nom à protéger. Le répertoire de sortie doit exister. Choisir `08-SAUVEGARDE` pour une action de sauvegarde.

```powershell
$ErrorActionPreference = 'Stop'
$destination = (Resolve-Path 'OS\Windows\03-CONFIGURATION').Path
$objet = [guid]::NewGuid().ToString('N') + '.age'
$travail = Join-Path ([IO.Path]::GetTempPath()) ('handbook-' + [guid]::NewGuid().ToString('N'))
$temporaire = Join-Path $destination ('.pending-' + [guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($travail) | Out-Null

try {
    $archive = Join-Path $travail 'archive.tar.gz'
    tar.exe -czf $archive -C 'C:\chemin\parent' 'source'
    if ($LASTEXITCODE -ne 0) { throw 'Création du tar refusée.' }

    age.exe -p -o $temporaire $archive
    if ($LASTEXITCODE -ne 0) { throw 'Chiffrement refusé.' }

    $final = Join-Path $destination $objet
    [IO.File]::Move($temporaire, $final)
    Write-Output $final
}
finally {
    if (Test-Path -LiteralPath $temporaire) { Remove-Item -LiteralPath $temporaire -Force }
    Remove-Item -LiteralPath $travail -Recurse -Force
}
```

L’objet final est publié après réussite du chiffrement, sans écrasement d’un objet existant. Les noms et fichiers cachés présents dans le tar restent chiffrés. Le temporaire en clair est supprimé à la fin normale ; sa suppression n’est pas une garantie d’effacement physique. Utiliser un profil et un stockage locaux convenablement protégés.

## Déchiffrer et retrouver les noms

Choisir un objet existant et saisir sa phrase secrète à l’invite. Le tar déchiffré et les fichiers récupérés restent hors dépôt.

```powershell
$ErrorActionPreference = 'Stop'
$objet = (Resolve-Path 'OS\Windows\03-CONFIGURATION\IDENTIFIANT.age').Path
$travail = Join-Path ([IO.Path]::GetTempPath()) ('handbook-' + [guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($travail) | Out-Null
$archive = Join-Path $travail 'archive.tar.gz'
$contenu = Join-Path $travail 'contenu'

try {
    age.exe --decrypt --output $archive $objet
    if ($LASTEXITCODE -ne 0) { throw 'Déchiffrement refusé.' }

    [IO.Directory]::CreateDirectory($contenu) | Out-Null
    tar.exe -xkzf $archive -C $contenu
    if ($LASTEXITCODE -ne 0) { throw 'Extraction refusée.' }
    Write-Output ('Récupération locale : ' + $contenu)
}
finally {
    if (Test-Path -LiteralPath $archive) { Remove-Item -LiteralPath $archive -Force }
}
```

Remplacer `IDENTIFIANT.age` par le vrai nom opaque. N’extraire que les archives attendues et de confiance. Les fichiers retrouvent leurs noms sous `contenu/` ; ne pas écraser une configuration active. Contrôler les ACL Windows et les différences de configuration avant application. Les fichiers récupérés persistent pour vérification ; les effacer manuellement s’ils ne sont plus utiles.

## Limites observées

Un ancien test automatique du mode à identité ([encryption.yml](../../.github/workflows/encryption.yml)) teste le chiffrement à clé publique sur un exécuteur GitHub `windows-latest` avec Windows PowerShell 5.1 et PowerShell 7, `bsdtar 3.8.9`, age `v1.3.2`, et des données fictives : accents, fichier caché, dossier vide, sous-dossier. Ce n'est pas un essai sur votre poste.

- **Noms hors page de code.** `tar.exe` plante (code `-1073741819`, sans message) sur un nom de fichier contenant des caractères japonais. Les accents français passent. Éviter les noms avec des caractères hors de la page de code Windows avant archivage, ou chiffrer depuis Linux. Cette limite n'existe pas dans la procédure Bash, testée avec des noms japonais.
- **Deux `tar.exe` dans le PATH.** Sur l'exécuteur, `C:\Windows\system32\tar.exe` (bsdtar) précède `C:\Program Files\Git\usr\bin\tar.exe` (GNU tar). Si l'ordre est inversé sur un poste, vérifier avec `Get-Command tar.exe -All` ; GNU tar interprète `C:` dans un chemin d'archive comme un hôte distant.
- **Windows PowerShell 5.1 et stderr.** Avec `$ErrorActionPreference = 'Stop'`, tout message d'un programme natif sur stderr devient une erreur, même avec `2>$null`. Les commandes ci-dessus n'en produisent pas en fonctionnement normal ; le test enveloppe seulement les cas où age écrit un avertissement.

Ces exemples ne dépendent pas de WSL.
