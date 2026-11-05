# Aller-retour de chiffrement age + tar (commandes de OUTILS/CHIFFREMENT/windows.md)
# avec des donnees fictives et une cle jetable. Compatible Windows PowerShell 5.1 et PowerShell 7.
# Fichier volontairement ASCII : les noms Unicode sont construits avec [char].
$ErrorActionPreference = 'Stop'

function Fail([string]$message) { throw "ECHEC : $message" }
function Native([string]$what) { if ($LASTEXITCODE -ne 0) { Fail $what } }
# Windows PowerShell 5.1 transforme toute ecriture sur stderr d'un programme natif en erreur
# quand $ErrorActionPreference vaut Stop : on l'assouplit pour les appels dont stderr est attendu.
function Quiet([scriptblock]$commande) {
    $avant = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { $null = & $commande 2>&1 } finally { $ErrorActionPreference = $avant }
}

Write-Output ('PowerShell ' + $PSVersionTable.PSVersion)
Get-Command tar.exe -All | ForEach-Object { Write-Output ('tar.exe : ' + $_.Source) }
tar.exe --version | Select-Object -First 1
age.exe --version

$racine = Join-Path ([IO.Path]::GetTempPath()) ('handbook-test-' + [guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($racine) | Out-Null
Push-Location $racine

try {
    # Cle jetable, creee et detruite dans ce test.
    $identiteFichier = Join-Path $racine 'identite.txt'
    $autreFichier = Join-Path $racine 'autre-identite.txt'
    Quiet { age-keygen.exe -o $identiteFichier }; Native 'age-keygen'
    Quiet { age-keygen.exe -o $autreFichier }; Native 'age-keygen (autre)'
    $publique = age-keygen.exe -y $identiteFichier; Native 'age-keygen -y'
    [IO.File]::WriteAllText((Join-Path $racine '.age-recipients'), ($publique + "`n"), (New-Object Text.UTF8Encoding($false)))

    # Donnees fictives : noms Unicode, fichier cache, dossier vide, sous-dossier.
    # Accents courants (page de code Windows 1252). Les caracteres hors page de code, comme le
    # japonais, font planter bsdtar 3.8.9 (voir OUTILS/CHIFFREMENT/windows.md) : ils ne sont testes que sous Linux.
    $e = [string][char]0x00E9; $u = [string][char]0x00FC
    $cc = ([string][char]0x00E7) + ([string][char]0x00F1) + ([string][char]0x0153)
    $parent = Join-Path $racine 'parent'
    $source = Join-Path $parent 'source'
    $profond = Join-Path $source ("r${e}pertoire $e $u\sous dossier")
    [IO.Directory]::CreateDirectory((Join-Path $racine 'OS\Windows\03-CONFIGURATION')) | Out-Null
    [IO.Directory]::CreateDirectory((Join-Path $source 'dossier-vide')) | Out-Null
    [IO.Directory]::CreateDirectory($profond) | Out-Null
    $utf8 = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText((Join-Path $source "note $e $u $cc.txt"), "contenu fictif`n", $utf8)
    [IO.File]::WriteAllText((Join-Path $source '.cache'), "cache`n", $utf8)
    [IO.File]::WriteAllText((Join-Path $profond 'fichier.txt'), "profond`n", $utf8)

    # Chiffrement (bloc "Chiffrer un fichier ou dossier").
    $destination = (Resolve-Path 'OS\Windows\03-CONFIGURATION').Path
    $destinataires = (Resolve-Path '.age-recipients').Path
    $objet = [guid]::NewGuid().ToString('N') + '.age'
    $travail = Join-Path ([IO.Path]::GetTempPath()) ('handbook-' + [guid]::NewGuid().ToString('N'))
    $temporaire = Join-Path $destination ('.pending-' + [guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($travail) | Out-Null
    try {
        $archive = Join-Path $travail 'archive.tar.gz'
        tar.exe -czf $archive -C $parent 'source'
        if ($LASTEXITCODE -ne 0) { throw 'Creation du tar refusee.' }

        age.exe -R $destinataires -o $temporaire $archive
        if ($LASTEXITCODE -ne 0) { throw 'Chiffrement refuse.' }

        $final = Join-Path $destination $objet
        [IO.File]::Move($temporaire, $final)
    }
    finally {
        if (Test-Path -LiteralPath $temporaire) { Remove-Item -LiteralPath $temporaire -Force }
        Remove-Item -LiteralPath $travail -Recurse -Force
    }

    if ($objet -notmatch '^[0-9a-f]{32}\.age$') { Fail "nom d'objet non opaque : $objet" }
    $octets = [IO.File]::ReadAllBytes($final)
    $entete = [Text.Encoding]::ASCII.GetString($octets, 0, 21)
    if ($entete -ne 'age-encryption.org/v1') { Fail 'en-tete age absent' }
    $brut = [Text.Encoding]::GetEncoding(28591).GetString($octets)
    if ($brut.Contains('fictif') -or $brut.Contains('note')) { Fail 'contenu ou nom en clair' }
    if (Get-ChildItem -LiteralPath $destination -Force -Filter '.pending-*') { Fail 'temporaire non supprime' }
    # Le deplacement ne doit pas ecraser un objet existant.
    $doublon = Join-Path $destination 'doublon.tmp'
    [IO.File]::WriteAllText($doublon, 'x')
    $ecrase = $false
    try { [IO.File]::Move($doublon, $final); $ecrase = $true } catch { }
    if ($ecrase) { Fail "ecrasement d'un objet existant" }

    # Dechiffrement (bloc "Dechiffrer et retrouver les noms").
    $objetChemin = (Resolve-Path $final).Path
    $travail2 = Join-Path ([IO.Path]::GetTempPath()) ('handbook-' + [guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($travail2) | Out-Null
    $archive2 = Join-Path $travail2 'archive.tar.gz'
    $contenu = Join-Path $travail2 'contenu'
    try {
        age.exe --decrypt --identity $identiteFichier --output $archive2 $objetChemin
        if ($LASTEXITCODE -ne 0) { throw 'Dechiffrement refuse.' }
        [IO.Directory]::CreateDirectory($contenu) | Out-Null
        tar.exe -xkzf $archive2 -C $contenu
        if ($LASTEXITCODE -ne 0) { throw 'Extraction refusee.' }

        # Comparaison : memes chemins relatifs (cache et dossier vide inclus) et memes empreintes.
        function Inventaire([string]$base) {
            Get-ChildItem -LiteralPath $base -Recurse -Force | ForEach-Object {
                $rel = $_.FullName.Substring($base.Length).TrimStart('\')
                if ($_.PSIsContainer) { "D $rel" } else { "F $rel " + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
            } | Sort-Object
        }
        $avant = Inventaire $source
        $apres = Inventaire (Join-Path $contenu 'source')
        if ($null -ne (Compare-Object $avant $apres)) { Fail 'contenu recupere different de l''original' }
        if (-not (Test-Path -LiteralPath (Join-Path $contenu 'source\.cache'))) { Fail 'fichier cache perdu' }
        if (-not (Test-Path -LiteralPath (Join-Path $contenu 'source\dossier-vide'))) { Fail 'dossier vide perdu' }

        # Une autre identite ne doit rien dechiffrer.
        $mauvais = Join-Path $travail2 'mauvais.tar.gz'
        Quiet { age.exe --decrypt --identity $autreFichier --output $mauvais $objetChemin }
        if ($LASTEXITCODE -eq 0) { Fail 'dechiffrement accepte avec une autre identite' }
    }
    finally {
        Remove-Item -LiteralPath $travail2 -Recurse -Force
    }

    Write-Output 'Aller-retour Windows valide.'
}
finally {
    Pop-Location
    Remove-Item -LiteralPath $racine -Recurse -Force -ErrorAction SilentlyContinue
}

# Le dernier appel natif est un dechiffrement volontairement refuse : sans cette remise a zero,
# $LASTEXITCODE (1) deviendrait le code de sortie du script malgre un test reussi.
# Les echecs, eux, levent une exception et terminent le script en erreur.
$global:LASTEXITCODE = 0
