# Volume matériel PCM, OSD et QSbar sous Ryoku

Résumé : sous Ryoku (niri), sur la sortie analogique interne du Dell, les touches de volume, le widget QSbar, le panneau de volume et l'OSD règlent le contrôle ALSA `PCM` ; les autres sorties restent pilotées par PipeWire. Les adaptations se réinstallent avec l'installateur audio.

- Statut : adaptations réalisées le 2026-11-08 après une installation fraîche (helpers, liaisons PCM des touches, du widget et du panneau, événement OSD) ; widget et panneau confirmés par l'utilisateur le 2026-11-07, conflit visuel de l'OSD corrigé le 2026-11-08 sans confirmation. **Ces adaptations sont absentes de l'installation du 2026-11-13** : voir « Dernière vérification ».
- Date : 2026-11-13.
- Dernière vérification : 2026-11-13 sur la machine (relevé de l'agent, sans essai d'écoute) : PipeWire 1.6.11, EasyEffects 8.3.2 ; `ryoku-alsa-levels.service` et `easyeffects.service` actifs ; `ryoku-volume`, `ryoku-audio-output`, `ryoku-audio-lab` et les overlays `PcmVolume.qml` introuvables ; aucun fichier `hda-jack-retask`, `80-ryoku-audio-smart-filters.conf` ni `82-ryoku-alc289-keep-headphone-path.conf` ; ALSA : `Speaker` 100 % ON, `Headphone` 100 % OFF, `PCM` 99 %.
- Portée : Arch Linux, Ryoku sous Niri, PipeWire ; test réalisé sur un Dell Latitude 7440.
- Environnements testés : EasyEffects 8.3.2, PipeWire 1.6.10, raccourcis Niri et barre Quickshell Ryoku.
- Configuration observée après installation fraîche le 2026-11-08 : la sortie par défaut est `alsa_output.pci-0000_00_1f.3.analog-stereo`. Les fichiers HDA `/etc/modprobe.d/hda-jack-retask.conf` et `/lib/firmware/hda-jack-retask.fw`, la règle `80-ryoku-audio-smart-filters.conf` et les helpers `ryoku-volume`/`ryoku-audio-output` étaient absents. ALSA exposait `Master`, `Headphone`, `Speaker` et `PCM`, sans `Bass Speaker` ; le relevé montrait `Master`/`Speaker` à 100 %, `Headphone` à 0 % et coupé, `PCM` à 71 %. Les helpers, les liaisons PCM des touches/widget/panneau et le signal de volume vers l'OSD sont maintenant installés dans les fichiers utilisateur et leurs overlays. EasyEffects était installé et actif pendant le relevé ; le sink physique restait la sortie par défaut.
- Fiches liées : le [matériel Dell et les haut-parleurs supérieurs](../../../02-SYSTEME/MACHINES/portable-dell/02-SYSTEME/audio-haut-parleurs-superieurs.md) et l'[historique des essais audio](../../09-NOTE/audio-historique-easyeffects-smart-filters.md).

## Réglage du helper de volume

Le helper utilisateur `~/.local/bin/ryoku-audio-output` traite directement les raccourcis `up` et `down` avec `amixer -c PCH sset PCM 5%+` ou `5%-` lorsque la sortie PipeWire par défaut est la sortie analogique interne du Dell. Pour un sink AirPods `bluez_output.*`, il règle directement le sink PipeWire par pas de 5 % avec `wpctl`, sans rechercher l'identifiant dans tout le graphe. Ces chemins directs évitent le parcours de graphe à chaque appui et envoient l'OSD en arrière-plan afin de ne pas retarder le changement du gain. Les sorties virtuelles gardent la résolution complète du chemin vers le sink matériel.

Pour les sorties virtuelles et l'action `mute`, le helper résout la cible ainsi :

1. Pendant une lecture EasyEffects, il repère dans `pw-link -l` le sink relié à `ee_soe_output_level:output_FL`.
2. Si le défaut est l'entrée d'un smart filter WirePlumber (`effect_input.ryoku-*`), il suit le lien de sortie correspondant jusqu'au sink physique.
3. Sinon, il cible le sink physique renvoyé par `pactl get-default-sink`, qui suit la sortie sélectionnée par WirePlumber.
4. Si EasyEffects est relancé et garde `easyeffects_sink` comme défaut avant que sa chaîne de sortie soit liée, il utilise `outputDevice` dans `~/.config/easyeffects/db/easyeffectsrc` en secours.
5. Il résout le nom en identifiant PipeWire à partir de `wpctl status -n`, puis ajuste le volume ou la sourdine avec `wpctl`.

Un wrapper utilisateur `~/.local/bin/ryoku-volume` appelle ce helper pour les commandes `up` et `down`, avant `/usr/bin` dans le `PATH`. Les raccourcis Niri de hausse et de baisse appellent `ryoku-volume`; le raccourci de sourdine appelle directement `wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle`. Les deux fichiers de configuration à conserver sont `~/.config/niri/rebinds.kdl` et `~/.config/ryoku/user_edits/niri/rebinds.kdl`.

Comme l'OSD Ryoku écoute normalement le volume du sink par défaut, le helper lui envoie le niveau adapté à la sortie contrôlée (PCM pour les haut-parleurs internes, sink PipeWire pour les autres sorties) et l'état muet avec :

```bash
qs ipc --config shell call osd showVolume <pourcentage> <true-ou-false>
```

`OsdFeed.qml` et `OsdSource.qml` mémorisent brièvement cette valeur pour afficher immédiatement le bon niveau et déclencher le cadre. Pour les haut-parleurs internes, `OsdSource.qml` retombe ensuite sur la lecture périodique de `PCM` par `PcmVolume`, pas sur le volume PipeWire du sink ALSA. Le niveau reste ainsi stable jusqu'à la fin de l'animation de disparition de l'OSD. Les autres sorties continuent d'afficher leur volume PipeWire. Dans l'ancien mode EasyEffects, le sink virtuel restait actif et les règles d'autoload pour les haut-parleurs et les AirPods restaient inchangées.

Correction du 2026-11-08 : pour la sortie interne PCH, les événements de volume PipeWire sont ignorés pour l'effacement de la valeur PCM de l'OSD, car le niveau PipeWire du sink peut rester à 100 % alors que `PCM` change. Les fichiers utilisateur et l'overlay ont été rechargés avec `ryoku-shell reload` ; le résultat visuel reste à confirmer par l'utilisateur.

### Barre QS après rechargement

Un essai a remplacé le `DeferredFileView` de `BarCatalog.qml` par un `FileView` bloquant ; il a modifié le rendu de QSbar et a été retiré le 2026-11-07. Le fichier actif est revenu à la version fournie par Ryoku. Si le catalogue est incomplet après un rechargement, réétudier la migration du layout avant de réappliquer ce changement.

### Indicateur de volume QSbar

Depuis le 2026-11-07, le chiffre du widget audio QSbar suit le niveau `PCM` ALSA lorsque le sink par défaut commence par `alsa_output.pci-0000_00_1f.3.`. Le singleton `PcmVolume.qml` relit `PCM` avec `amixer -c PCH sget PCM` chaque seconde, seulement lorsque cette sortie est active ; cette lecture ponctuelle évite de laisser un processus d'écoute ALSA après un rechargement Quickshell. Le nom de carte suit `RYOKU_PCM_CARD` si cette variable est définie, comme le helper des touches. Pour les autres sorties, le widget garde le volume PipeWire. La molette du widget appelle `ryoku-volume` sur la sortie interne ; le curseur et la molette du panneau de volume règlent aussi `PCM` en interne.

Les fichiers de cette adaptation sont `shell/audio/PcmVolume.qml`, `shell/audio/qmldir` et `shell/modules/bar/barstyles/qsbar/modules/AudioWidget.qml`, dans `~/.config/quickshell/` et `~/.config/ryoku/user_edits/quickshell/`. L'installateur audio conserve ces overlays dans `05-SCRIPT/AUDIO/`, les déploie dans `user_edits` et les applique aussi aux fichiers actifs.

Le panneau de volume ouvert par clic a ensuite été corrigé de la même façon : pour le sink analogique PCH, son curseur et sa molette écrivent `PCM` via `PcmVolume.setVolume()` et affichent le pourcentage PCM. Les autres sorties gardent le contrôle PipeWire. La sourdine reste celle du sink PipeWire ; le réglage PCM au-dessus de 100 % est désactivé pour les haut-parleurs internes. Fichiers actifs et overlays persistants : `shell/modules/bar/barstyles/qsbar/panels/VolumePanel.qml` et `shell/audio/PcmVolume.qml`. Après rechargement de Quickshell, l'utilisateur a confirmé que le résultat est correct (2026-11-07).

## Persistance et retour arrière

Le helper et son wrapper résident dans `~/.local/bin/`; les raccourcis source se trouvent dans les deux fichiers Niri indiqués plus haut. Les adaptations PCM du widget, du panneau et de l'OSD résident dans `~/.config/quickshell/` et `~/.config/ryoku/user_edits/quickshell/`. Conserver les overlays si le shell est réinstallé ou réinitialisé.

Pour revenir à l'ancien ciblage, restaurer les fichiers Niri et Quickshell depuis une copie de configuration, puis retirer `~/.local/bin/ryoku-audio-output` et `~/.local/bin/ryoku-volume`. Cela rétablit les raccourcis qui ciblent le sink par défaut et supprime l'affichage OSD matériel.

## Réinstallation du trajet audio

L'installateur documenté dans [Scripts Ryoku — Audio](../../05-SCRIPT/AUDIO/README.md) regroupe les filtres WirePlumber, les raccourcis PCM, les contrôles QSbar/panneau, et l'état ALSA de `Speaker`/`Master`. Le retask HDA de `0x14` est facultatif (`--retask-0x14`). Le script complet reste à valider sur une installation vierge.

## Références

- [Autoload EasyEffects par appareil](../../../../../../OUTILS/EASYEFFECTS/autoload-par-appareil.md) : profils séparés pour AirPods et haut-parleurs.
- [Preset Waves ON des haut-parleurs Dell](../../../02-SYSTEME/MACHINES/portable-dell/03-CONFIGURATION/easyeffects-modele-waves-on.md).
- [Haut-parleurs supérieurs et retask HDA du Dell](../../../02-SYSTEME/MACHINES/portable-dell/02-SYSTEME/audio-haut-parleurs-superieurs.md).
- [Historique audio : mode EasyEffects, routage natif et smart filters](../../09-NOTE/audio-historique-easyeffects-smart-filters.md).
