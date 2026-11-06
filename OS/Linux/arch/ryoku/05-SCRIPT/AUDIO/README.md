# Audio — Ryoku

Résumé : installateur pour retrouver le trajet audio du Dell Latitude 7440 : retask HDA `0x14`, filtres WirePlumber pour les haut-parleurs et les AirPods, volume des touches lié au PCM interne, et base ALSA sauvegardée.

- Statut : script rédigé depuis la configuration du Latitude 7440 de référence ; il n'a pas encore été exécuté ni validé sur une installation propre.
- Date : 2026-11-06
- Portée : Arch Linux, Ryoku, PipeWire, WirePlumber et Niri.
- Matériel visé : Dell Latitude 7440, Realtek ALC289, sous-identifiant codec `0x10280c0c`, carte ALSA `PCH`.
- Dépendances installées si manquantes : `pipewire`, `pipewire-alsa`, `pipewire-pulse`, `wireplumber`, `alsa-utils`, `alsa-tools`, `lsp-plugins-lv2`, `jq` et `ripgrep`.

## Installation

Lancer le script comme utilisateur de bureau, sans `sudo` :

```bash
~/system-handbook/OS/Linux/arch/ryoku/05-SCRIPT/AUDIO/installer-audio-latitude-7440.sh --dry-run
~/system-handbook/OS/Linux/arch/ryoku/05-SCRIPT/AUDIO/installer-audio-latitude-7440.sh
```

Le script vérifie Arch Linux, le modèle, le codec et son sous-identifiant avant de toucher aux fichiers. Il demande les droits administrateur pour installer les paquets, configurer le retask de démarrage et enregistrer l'état ALSA. Il sauvegarde chaque fichier remplacé sous `~/.local/state/ryoku-latitude-audio/backups/<horodatage>/`.

Si des AirPods sont connectés, leur sink PipeWire est détecté automatiquement. Sinon, l'installateur met en place le profil des haut-parleurs ; pour ajouter le profil des AirPods plus tard, les connecter puis relancer le script avec leur nom exact :

```bash
pactl list short sinks
~/system-handbook/OS/Linux/arch/ryoku/05-SCRIPT/AUDIO/installer-audio-latitude-7440.sh --airpods-sink bluez_output.ADRESSE.1
```

Remplacer `ADRESSE` par la partie correspondante du nom réel. Ce nom reste dans le fichier local WirePlumber ; l'asset livré ici ne contient pas l'adresse Bluetooth de l'appareil.

## Réglages appliqués

- Installe WirePlumber, PipeWire, le module ALSA et les plugins LV2 utilisés par les filtres.
- Active les sockets PipeWire et WirePlumber pour la session utilisateur.
- Installe les filtres intelligents dérivés des presets EasyEffects de référence et la préférence codecs Bluetooth du profil Ryoku. Le preset EasyEffects d'origine reste intact ; cette traduction WirePlumber ne reproduit pas exactement tous ses étages.
- Installe `ryoku-audio-output` et `ryoku-volume`. Si `~/.config/niri/rebinds.kdl` contient une seule ligne de chaque raccourci, remplace uniquement les commandes hausse/baisse par `ryoku-volume up/down`. La sourdine reste pilotée par PipeWire. Si le format est différent, le fichier n'est pas modifié et le script affiche les raccourcis à ajouter manuellement.
- Active l'interrupteur `Speaker`, garde `Master` et `Bass Speaker` à 100 %, puis sauvegarde l'état ALSA avec `alsactl`. Le niveau `PCM` est laissé intact : c'est la commande de volume pour les haut-parleurs internes et le script ne doit pas augmenter le niveau d'écoute sans demande.
- Installe l'override HDA correspondant à la broche `0x14` (`0x90170150`, `Internal speaker`) et son firmware. Le redémarrage du PC est nécessaire avant de vérifier cette sortie.
- Redémarre WirePlumber si sa configuration a changé.

La stratégie des filtres intelligents correspond à la propriété `filter.smart.target` documentée par WirePlumber : [documentation officielle WirePlumber — Smart Filters](https://pipewire.pages.freedesktop.org/wireplumber/policies/smart_filters.html).

## Vérification manuelle après redémarrage

```bash
grep -E 'Codec:|Subsystem Id:' /proc/asound/card*/codec#*
grep -E '0x14|user_pin_configs' /proc/asound/card*/codec#*
amixer -c PCH scontents
pactl get-default-sink
```

Vérifier que `Speaker` et `Bass Speaker` sont activés, que `Master` et `Bass Speaker` sont à 100 %, et régler le niveau d'écoute avec `PCM` ou les touches de volume. Tester la contribution des haut-parleurs du haut pendant la même lecture et à niveau PCM constant. Le guide complet consigne les observations et limites : [routage audio natif et volume matériel](../../07-RESOLUTION/AUDIO/volume-physique-avec-easyeffects.md).

## Retour arrière

Les fichiers remplacés sont copiés dans le dossier de sauvegarde annoncé à la fin du script. Pour annuler, restaurer chaque copie à son chemin précédent. Si un fichier HDA n'existait pas avant l'installation, retirer `/etc/modprobe.d/hda-jack-retask.conf` et `/lib/firmware/hda-jack-retask.fw`, puis redémarrer. Restaurer ou retirer les fichiers WirePlumber et helper installés, et remettre les deux lignes Niri depuis la sauvegarde si le script les a modifiées.

Voir les [instructions IA](00-AGENTS.md) et le [sommaire des scripts Ryoku](../README.md).
