# GeForce NOW : interface trop petite sous XWayland

- Résumé : sur Omarchy avec Hyprland, le client GeForce NOW Flatpak peut afficher une interface trop petite ; un zoom CEF de 150 % a corrigé la taille sur la machine testée.
- Statut : résolu (confirmé par l'utilisateur).
- Date : 2026-11-10.
- Portée : Arch Linux, Omarchy, Hyprland, GeForce NOW Flatpak `com.nvidia.geforcenow`.
- Environnements testés : GeForce NOW 2.0.90.126, écran 1920 × 1200, échelle Hyprland 1,33 et client sous XWayland avec `xwayland:force_zero_scaling` activé.
- Prérequis et exclusions : avoir lancé le client au moins une fois ; la valeur 150 % correspond aux préférences de l'utilisateur et peut devoir être adaptée à un autre écran.

## Problème et diagnostic

Les menus et textes du client sont trop petits. Le client utilise Chromium Embedded Framework (CEF), et le réglage Qt de Plex ne s'applique pas ici. Le zoom de l'interface peut être enregistré dans les préférences CEF locales, sans changer l'échelle de toutes les applications.

## Procédure

Fermer complètement GeForce NOW, puis exécuter dans un shell bash :

```bash
python3 - <<'PY'
import json
import math
from pathlib import Path

path = Path.home() / '.var/app/com.nvidia.geforcenow/.local/state/NVIDIA/GeForceNOW/CefCache/Default/Preferences'
data = json.loads(path.read_text())
data.setdefault('partition', {}).setdefault('default_zoom_level', {})['x'] = math.log(1.5) / math.log(1.2)
path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
PY
```

Relancer GeForce NOW. Pour essayer une autre taille, remplacer `1.5` par le facteur souhaité ; la valeur enregistrée est un niveau de zoom logarithmique CEF.

## Validation

Le 2026-11-10, l'utilisateur a confirmé que 150 % convenait après relance. La résolution et la qualité d'une session de jeu n'ont pas été vérifiées.

## Persistance et retour arrière

Une mise à jour ou une réinitialisation du cache peut écraser ce réglage. Pour supprimer uniquement le zoom ajouté, fermer le client puis exécuter :

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path.home() / '.var/app/com.nvidia.geforcenow/.local/state/NVIDIA/GeForceNOW/CefCache/Default/Preferences'
data = json.loads(path.read_text())
data.get('partition', {}).get('default_zoom_level', {}).pop('x', None)
path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
PY
```

Relancer ensuite le client.

## Références

- [GeForce NOW Scaling Patch for Linux](https://github.com/Kermit83Lair/gfnow-tools) : contournement communautaire utilisant le zoom CEF.
- [Plex Desktop : taille et netteté sous XWayland](plex-desktop-echelle-xwayland.md) : réglage propre au client Qt.
