# Reprendre les mesures Waves du Dell Latitude 7440

- Résumé : prérequis, disposition des dossiers et ordre des campagnes pour refaire ou prolonger les mesures Waves sans repartir de zéro, à partir des scripts et protocoles conservés.
- Statut : proposé (les scripts n'ont pas été relancés depuis cette copie)
- Date : 2026-11-05
- Portée : Windows 11 pour l'acquisition, n'importe quel poste avec Python pour l'analyse et l'ajustement ; Dell Latitude 7440, Realtek, Waves MaxxAudio 2.0.54.0.
- Environnements testés : les scripts ont été exécutés par des IA sous Windows 11 (build 26300) avec Python 3.13.9 embarqué. Aucune relance depuis ce dépôt.
- Prérequis et exclusions : Waves MaxxAudio installé et piloté par son interface (UI Automation) ; l'acquisition ne fonctionne ni sous Linux ni avec un autre matériel sans adaptation.

## But ou problème

Obtenir à nouveau un signal numérique de référence « Windows avec Waves » à plusieurs niveaux, puis en déduire un preset EasyEffects, sans reconstruire la méthode.

## Diagnostic

Ce qui a été établi par les campagnes (détails dans les rapports) :

- La capture loopback WASAPI en mode partagé voit le traitement Waves ; c'est un signal numérique envoyé à l'ampli, pas une mesure acoustique des haut-parleurs.
- Le comportement dépend du niveau (compression, gain, stéréo) : un seul convolver ne suffit pas, d'où un modèle EQ Mid/Side, compresseur multibande et limiteur.
- Une mesure acoustique avec microphone reste nécessaire pour conclure sur le son réellement entendu.

## Procédure ou utilisation

### Disposition attendue

Les scripts résolvent leurs chemins par rapport à leur propre dossier. Recréer ce dossier de travail avec les noms d'origine :

| Dossier du dépôt | Nom d'origine dans le dossier de travail |
| --- | --- |
| [windows-wasapi](windows-wasapi/README.md) | `Mesures-Windows-WASAPI` |
| [effets-isoles](effets-isoles/README.md) | `Mesures-Effets-Isoles` |
| [profil-actuel](profil-actuel/README.md) | `Mesures-Profil-Actuel-20261030` |
| [musique](musique/README.md) | `Mesures-Musique` (avec `model/` et `reference/`) |

Les campagnes suivantes utilisent le Python local de la première (`../Mesures-Windows-WASAPI/tools/python/python.exe`).

### Prérequis

1. Sous Windows, lancer `bootstrap-tools.ps1` dans le dossier `Mesures-Windows-WASAPI` : il recrée un Python 3.13.9 embarqué local, sans toucher au Python du système. Les dépendances sont dans `requirements-lock.txt`, dont `pyloudnorm==0.2.0` (sonie BS.1770, utilisé par `prepare_sources.py`, `analyze.py` et le protocole approfondi) : la version vient du Python embarqué des campagnes d'origine.
2. Prévoir ffmpeg pour la contre-vérification de sonie du profil approfondi, et des extraits musicaux FLAC pour `prepare_sources.py` (6 extraits ont été utilisés : instrumental, musique 96 kHz, chanson 24 bits, ultra 192 kHz, voix, jeu de test).
3. Relever l'identifiant du périphérique de rendu Realtek et l'état initial de Waves avant toute modification, et mettre la sortie physique en muet pendant les captures. Chaque script restaure ensuite volume, mute et réglages dans un bloc `finally`.

### Ordre conseillé

1. Lire le [protocole](protocole/README.md) et le [rapport WASAPI](windows-wasapi/RAPPORT-WASAPI.md), puis exécuter la première campagne (inventaire, paire Waves ON/OFF, répétabilité).
2. [Effets isolés](effets-isoles/README.md) : la méthode et le plan des 36 captures y sont décrits.
3. [Profil approfondi](profil-actuel/README.md) : balayage de tous les volumes, puis séries longues.
4. [Musique](musique/README.md) : `prepare_sources.py`, `acquire.py`, `analyze.py`, puis `model/` (`stage1_curves.py`, `fit_model.py`, `validate_model.py`, `export_preset.py`) pour régénérer les presets.

## Validation

Non rejouée depuis ce dépôt. Les rapports donnent les contrôles réalisés lors des campagnes d'origine : l'erreur du modèle Mid par tiers d'octave (2,1 dB RMS) est une simulation Python, pas une mesure sous EasyEffects.

## Persistance et maintenance

Une mise à jour de Waves, du pilote Realtek ou de l'interface peut casser le pilotage UI Automation (`waves-ui.ps1`) : revérifier les contrôles avant de relancer. Versions mesurées : [windows-versions.json](windows-wasapi/windows-versions.json). `stage1_curves.py` lit en option une courbe de référence de l'ancien candidat SST (`candidate-response-linux.csv`), qui n'est pas conservée ; cette comparaison est seulement informative.

## Sauvegarde et retour arrière

Aucune donnée brute n'est versionnée. Pour conserver captures et manifestes, les chiffrer avec age selon [la procédure](../../../CHIFFREMENT.md) et les ranger hors de ce dépôt. Les scripts de campagne restaurent eux-mêmes l'état audio ; en cas d'arrêt forcé, vérifier à la main le volume, le mute et les réglages Waves.

## Références

- [Modèle Waves ON](MODELE-WAVES.md).
- [Protocole de départ](protocole/PROMPT-WINDOWS-WASAPI.md).
