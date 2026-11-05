# Modèle Waves ON — preset EasyEffects (ajusté sur des mesures musicales)

- Résumé : modèle Waves ON ajusté sur les captures musicales : chaîne EasyEffects, qualité de l'ajustement et limites.
- Statut : proposé (ajusté sur des mesures, rendu non validé par écoute A/B)
- Date : 2026-11-05

Ce preset reproduit **le signal numérique que Windows envoie vers l'ampli quand Waves est ON** (profil 50/35/35), tel que mesuré en loopback WASAPI sur 6 extraits musicaux/voix × 3 niveaux (`Mesures-Musique/`). Ce n'est pas une mesure acoustique des haut-parleurs.

## Fichiers

- `Dell Latitude 7440 - modèle Waves ON (mesures musique).json` : même niveau numérique que Windows ON.
- `... , -6 dB).json` : identique avec 6 dB de moins en sortie (point de départ conseillé).
- Générateurs : `Mesures-Musique/model/` (`stage1_curves.py`, `fit_model.py`, `validate_model.py`, `export_preset.py`), paramètres dans `model/model.json`.

## Chaîne (effets de sortie)

1. Stereo Tools `LR > MS` → 2. Égaliseur 20 bandes, canaux séparés (gauche = Mid, droite = Side) → 3. Stereo Tools `MS > LR` → 4. Compresseur multibande 5 bandes (coupures 120 / 500 / 2000 / 6000 Hz) → 5. Limiteur (-0,3 dB, lookahead 5 ms).

Ce que l'ajustement a trouvé : graves ramenés en mono (Side jusqu'à -23 dB sous 100 Hz) et fortement relevés (Mid jusqu'à +10 dB, en plus de la compression), médiums élargis (Side environ +5 à +6 dB entre 1 et 4 kHz, Mid environ +1 à +3 dB), compression forte (ratios 2,8:1 à 8:1) et plafond de sonie vers -8 LUFS.

## Qualité du modèle (simulation Python sur les 18 captures, pas EasyEffects)

| Mesure | Modèle | Sans traitement |
| --- | --- | --- |
| Erreur Mid par tiers d'octave, 63 Hz–12,5 kHz (RMS) | 2,1 dB | 9,8 dB |
| Erreur Side, morceaux stéréo (RMS) | 3,0 dB | — |
| Sonie (LUFS), écart moyen / max | -0,9 / 1,9 dB | — |

Le modèle est un peu plus bas que Windows (≈ 1 dB).

## Installation

Copier les JSON dans `~/.local/share/easyeffects/output/`, puis les charger dans EasyEffects (effets de sortie) ou `easyeffects --load-preset '<nom>'`.

## Limites

- **Non testé dans EasyEffects 8.3.0** : les clés viennent des sources (kcfg/`*_preset.cpp`), mais le chargement réel et le rendu sonore restent à vérifier. Si un plugin ne se charge pas, l'erreur d'import indiquera la clé fautive.
- Le compresseur LSP n'est pas identique à ma simulation (détection, lissage, coupures). Les temps d'attaque/relâchement (20/200 ms) n'ont pas été ajustés.
- Les valeurs de l'EQ Mid/Side sont ajustées sur 6 extraits dont 3 réellement stéréo. À revalider sur d'autres morceaux.
- Le niveau est celui de Windows ON, **très fort** (≈ +14 à +23 LU par rapport à OFF). Commencer à faible volume avec la variante -6 dB.
- Non mesuré : haut-parleurs, ampli, protections thermiques/mécaniques. Un test d'écoute A/B à volume égal reste nécessaire.
- Hypothèse : Linux envoie au codec le même signal numérique que Windows après Waves.
