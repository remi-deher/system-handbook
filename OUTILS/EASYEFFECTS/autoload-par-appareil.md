# EasyEffects : un preset par sortie audio (autoload)

- Résumé : charger automatiquement un preset EasyEffects pour des AirPods Bluetooth et un autre pour les haut-parleurs internes, avec les pièges rencontrés (nom de route localisé, liste de blocage, preset qui persiste).
- Statut : testé
- Date : 2026-11-05
- Portée : Linux, EasyEffects 8.3.2, PipeWire et WirePlumber, session en français ; vérifié sur le Dell Latitude 7440 avec des AirPods Pro 3.
- Environnements testés : bash et fish. La bascule a été vérifiée en déconnectant et reconnectant les AirPods pendant une lecture ; le rendu des AirPods est confirmé par l'utilisateur.
- Prérequis et exclusions : EasyEffects en mode service (`--service-mode`). Les noms de route sont ceux de la locale du système ; un autre réglage de langue demande de renommer les fichiers.

## But ou problème

Appliquer un preset seulement quand une sortie précise est active (ici les AirPods Pro 3), et garder le preset d'origine sur les autres sorties.

## Diagnostic

Trois points ont empêché le premier essai :

1. **Liste de blocage.** Si le sink Bluetooth figure dans `outputSinkBlocklist` (section `[EffectsPipelines]` de `~/.config/easyeffects/db/easyeffectsrc`), EasyEffects ne traite pas cette sortie. Retirer la ligne.
2. **Nom de la route.** Le champ `device-profile` d'un fichier d'autoload n'est pas le nom technique du port (`headphone-output`) mais sa **description localisée**, celle que `pactl list sinks` affiche dans `Ports:` : « Casque audio » pour un sink Bluetooth, « Haut-parleurs » pour l'interne. Avec un mauvais nom, le journal indique : `Could not find an autoload profile for the device … and route …`.
3. **Le dernier preset persiste.** Sans autoload pour une sortie, EasyEffects garde le dernier preset chargé. Un preset AirPods resterait donc actif sur les haut-parleurs. Il faut un fichier d'autoload pour chaque sortie utilisée.

Le sink virtuel `easyeffects_sink` peut rester la sortie par défaut pour faire passer les flux par les effets et préserver l'autoload. Dans cette configuration, les raccourcis de volume qui ciblent `@DEFAULT_AUDIO_SINK@` règlent le sink virtuel, pas nécessairement la sortie matérielle qui reçoit le signal. Sous Ryoku, voir [les commandes de volume](../../OS/Linux/arch/ryoku/07-RESOLUTION/AUDIO/volume-pcm-osd-qsbar.md) et l'[historique des essais audio](../../OS/Linux/arch/ryoku/09-NOTE/audio-historique-easyeffects-smart-filters.md).

## Procédure ou utilisation

Shell : bash ou fish.

1. Copier le preset dans le dossier de sortie d'EasyEffects :

   ```bash
   mkdir -p ~/.local/share/easyeffects/output ~/.local/share/easyeffects/autoload/output
   cp "PRESETS/AirPods Pro 3.json" ~/.local/share/easyeffects/output/
   ```

2. Relever le nom du sink et la description du port, AirPods connectés :

   ```bash
   pactl list short sinks
   pactl list sinks | grep -E 'Name:|Ports:|^\s+[a-z-]+output'
   ```

3. Copier les modèles d'autoload et les adapter. Le fichier se nomme `<sink>:<route>.json`, avec le nom exact du sink et la description du port, et `preset-name` est le nom du preset sans l'extension :

   ```bash
   cp PRESETS/autoload-airpods-pro-3.json "$HOME/.local/share/easyeffects/autoload/output/bluez_output.<ADRESSE>.1:Casque audio.json"
   cp PRESETS/autoload-haut-parleurs.json "$HOME/.local/share/easyeffects/autoload/output/alsa_output.<SINK-INTERNE>:Haut-parleurs.json"
   ```

   Les guillemets sont nécessaires (espace dans le nom). Dans chaque fichier, mettre le même sink dans `device` et la même route dans `device-profile`.

4. Retirer le sink de `outputSinkBlocklist` s'il y figure, EasyEffects étant arrêté, puis relancer le service :

   ```bash
   easyeffects -q
   sed -i '/^outputSinkBlocklist=/d' ~/.config/easyeffects/db/easyeffectsrc
   easyeffects --hide-window --service-mode &
   ```

   Pour arrêter le processus de force, utiliser `pkill -x easyeffects` : `pkill -f easyeffects` peut aussi tuer le shell qui contient ce mot dans sa ligne de commande.

## Validation

Essai réel, avec une lecture en boucle pendant la bascule :

```bash
pw-dump | grep -oE 'ee_soe_[a-z_]+' | sort -u      # plugins de la chaîne active
pw-link -l | grep -A1 'ee_soe_output_level:output_FL'   # sortie réellement utilisée
journalctl --user -b | grep presets_autoload_manager     # décisions d'autoload
```

- Haut-parleurs internes : la chaîne Waves complète (`ee_soe_multiband_compressor` présent), sortie vers `alsa_output…`.
- AirPods reconnectés : seul `ee_soe_equalizer`, sortie vers `bluez_output…`.
- Les nœuds `ee_soe_*` n'existent que pendant une lecture : le filtre est délié quand aucune application ne joue.
- Changer le sink par défaut avec `pactl set-default-sink` n'a pas déclenché l'autoload ; la connexion ou la déconnexion de l'appareil l'a fait.
- `easyeffects --debug` active les messages détaillés (dans le journal utilisateur).

Non testé : l'option de preset de repli (« fallback ») d'EasyEffects pour les sorties sans autoload.

## Persistance et maintenance

Les fichiers d'autoload et les presets vivent dans `~/.local/share/easyeffects/`. Le fichier `easyeffectsrc` n'est réécrit qu'à certains événements ; les modifier avec le service arrêté. Une mise à jour d'EasyEffects peut changer le format ; relire alors les messages du journal.

## Sauvegarde et retour arrière

Sauvegarder `~/.config/easyeffects` avant de modifier `easyeffectsrc`. Pour revenir en arrière, supprimer les fichiers d'autoload et le preset, puis remettre au besoin `outputSinkBlocklist=<sink>` dans `[EffectsPipelines]`.

## Références

- [Presets et modèles](PRESETS/README.md).
- [Presets Waves ON du Dell](../../OS/Linux/arch/02-SYSTEME/MACHINES/portable-dell/03-CONFIGURATION/easyeffects-modele-waves-on.md).
