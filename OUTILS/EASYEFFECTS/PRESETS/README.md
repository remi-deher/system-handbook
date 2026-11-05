# Presets et modèles d'autoload

Preset de sortie pour des AirPods Pro 3 et deux fichiers d'autoload à adapter. Procédure : [autoload par appareil](../autoload-par-appareil.md).

## Contenu

- [AirPods Pro 3.json](AirPods%20Pro%203.json) : preset de sortie, un égaliseur IIR à 10 bandes (32 Hz à 16 kHz, Bell, Q 1,41, gains de +1,6 à +3,6 dB) et un gain d'entrée de -2,5 dB. Le format a été chargé par EasyEffects 8.3.2 ; l'écoute a été confirmée par l'utilisateur.
- [autoload-airpods-pro-3.json](autoload-airpods-pro-3.json) : modèle d'autoload pour un sink Bluetooth (`bluez_output.XX_XX_XX_XX_XX_XX.1`). Remplacer l'adresse par celle des écouteurs.
- [autoload-haut-parleurs.json](autoload-haut-parleurs.json) : modèle d'autoload pour les haut-parleurs internes, avec le preset Waves ON du Dell. Adapter le sink et le nom du preset.
- Presets Waves ON du Dell : [portable-dell](../../../OS/Linux/arch/02-SYSTEME/MACHINES/portable-dell/03-CONFIGURATION/easyeffects-modele-waves-on.md).

Voir les [instructions IA](AGENTS.md) et [l'index EasyEffects](../README.md).
