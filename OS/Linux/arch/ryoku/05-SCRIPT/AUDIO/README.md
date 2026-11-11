# Audio — Ryoku

Résumé : installateur du trajet audio du Dell Latitude 7440 : filtres WirePlumber pour les haut-parleurs et les AirPods, touches et contrôles QSbar/panneau liés au PCM interne, et base ALSA sauvegardée. Le retask HDA `0x14` est facultatif et désactivé par défaut.

- Statut : les contrôles PCM ont été déployés manuellement sur une installation fraîche le 2026-11-08 ; l'installateur complet reste à exécuter/valider. Le retask `0x14` est facultatif après une observation utilisateur montrant que le haut-parleur supérieur est audible via le contrôle ALSA `Headphone` sans retask.
- Date : 2026-11-08
- Portée : Arch Linux, Ryoku, PipeWire, WirePlumber et Niri.
- Matériel visé : Dell Latitude 7440, Realtek ALC289, sous-identifiant codec `0x10280c0c`, carte ALSA `PCH`.
- Dépendances installées si manquantes : `pipewire`, `pipewire-alsa`, `pipewire-pulse`, `wireplumber`, `alsa-utils`, `alsa-tools`, `lsp-plugins-lv2`, `jq` et `ripgrep`.

## Installation

Lancer le script comme utilisateur de bureau, sans `sudo` :

```bash
~/GitHub/system-handbook/OS/Linux/arch/ryoku/05-SCRIPT/AUDIO/installer-audio-latitude-7440.sh --dry-run
~/GitHub/system-handbook/OS/Linux/arch/ryoku/05-SCRIPT/AUDIO/installer-audio-latitude-7440.sh
```

Le script vérifie Arch Linux, le modèle, le codec et son sous-identifiant avant de toucher aux fichiers. Il demande les droits administrateur pour installer les paquets et enregistrer l'état ALSA ; il ne modifie pas les broches HDA par défaut. Ajouter `--retask-0x14` seulement si l'essai de sortie montre que le haut-parleur supérieur n'est pas accessible autrement. Il sauvegarde chaque fichier remplacé sous `~/.local/state/ryoku-latitude-audio/backups/<horodatage>/`.

Si des AirPods sont connectés, leur sink PipeWire est détecté automatiquement. Sinon, l'installateur met en place le profil des haut-parleurs ; pour ajouter le profil des AirPods plus tard, les connecter puis relancer le script avec leur nom exact :

```bash
pactl list short sinks
~/GitHub/system-handbook/OS/Linux/arch/ryoku/05-SCRIPT/AUDIO/installer-audio-latitude-7440.sh --airpods-sink bluez_output.ADRESSE.1
```

Remplacer `ADRESSE` par la partie correspondante du nom réel. Ce nom reste dans le fichier local WirePlumber ; l'asset livré ici ne contient pas l'adresse Bluetooth de l'appareil.

## Réglages appliqués

- Installe WirePlumber, PipeWire, le module ALSA et les plugins LV2 utilisés par les filtres.
- Active les sockets PipeWire et WirePlumber pour la session utilisateur.
- Installe les filtres intelligents dérivés des presets EasyEffects de référence et la préférence codecs Bluetooth du profil Ryoku. Le preset EasyEffects d'origine reste intact ; cette traduction WirePlumber ne reproduit pas exactement tous ses étages.
- Installe `ryoku-audio-output` et `ryoku-volume`. Si `~/.config/niri/rebinds.kdl` contient une seule ligne de chaque raccourci, remplace uniquement les commandes hausse/baisse par `ryoku-volume up/down`. La sourdine reste pilotée par PipeWire. Si le format est différent, le fichier n'est pas modifié et le script affiche les raccourcis à ajouter manuellement.
- Installe les adaptations audio Quickshell dans `~/.config/ryoku/user_edits/` et les applique aussi aux fichiers actifs : le widget QSbar, le panneau et l'OSD lisent/règlent `PCM` sur la sortie interne, tout en gardant PipeWire pour les autres sorties. Les touches, la molette du widget et le curseur/molette du panneau règlent `PCM` en interne. Les fichiers actifs sont sauvegardés avant remplacement et Quickshell est rechargé après installation.
- Avec `--retask-0x14`, installe l'override HDA (`0x14 0x90170150`, « Internal speaker ») et son firmware ; le redémarrage est nécessaire pour l'appliquer. Sans cette option, les fichiers de retask restent intacts.
- Active l'interrupteur `Speaker`, garde `Master` à 100 %, puis sauvegarde l'état ALSA avec `alsactl`. Si `Bass Speaker` existe, il est aussi gardé à 100 %. Le niveau `PCM` reste inchangé et sert au volume d'écoute.
- Redémarre WirePlumber si sa configuration a changé.

La stratégie des filtres intelligents correspond à la propriété `filter.smart.target` documentée par WirePlumber : [documentation officielle WirePlumber — Smart Filters](https://pipewire.pages.freedesktop.org/wireplumber/policies/smart_filters.html).

## Vérification manuelle après redémarrage

```bash
grep -E 'Codec:|Subsystem Id:' /proc/asound/card*/codec#*
grep -E '0x14|user_pin_configs' /proc/asound/card*/codec#*
amixer -c PCH scontents
pactl get-default-sink
```

Vérifier que `Speaker` est activé et que `Master` est à 100 %. Si le retask est activé et que `Bass Speaker` existe, vérifier aussi ce contrôle. Régler le niveau d'écoute avec `PCM` ou les touches de volume. Le haut-parleur supérieur a été signalé audible via `Headphone` sans retask sur une installation fraîche ; voir les observations et limites dans [routage audio natif et volume matériel](../../07-RESOLUTION/AUDIO/volume-physique-avec-easyeffects.md).

## Retour arrière

Les fichiers remplacés sont copiés dans le dossier de sauvegarde annoncé à la fin du script. Pour annuler, restaurer chaque copie à son chemin précédent. Si `--retask-0x14` a été utilisé et que ces fichiers n'existaient pas avant, retirer `/etc/modprobe.d/hda-jack-retask.conf` et `/lib/firmware/hda-jack-retask.fw`, puis redémarrer. Restaurer ou retirer les fichiers WirePlumber et helper installés, et remettre les deux lignes Niri depuis la sauvegarde si le script les a modifiées.

Voir les [instructions IA](00-AGENTS.md) et le [sommaire des scripts Ryoku](../README.md).
