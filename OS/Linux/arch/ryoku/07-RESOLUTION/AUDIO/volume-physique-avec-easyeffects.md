# Routage audio natif et volume matériel sous Ryoku

Résumé : WirePlumber choisit automatiquement entre les haut-parleurs et les AirPods, tandis que des smart filters appliquent le profil audio adapté. Le helper Ryoku règle le volume du sink matériel actif, avec ou sans EasyEffects.

- Statut : résolu ; l'utilisateur a confirmé la bascule automatique dans les deux sens et le fonctionnement du bouton de volume avec le routage natif.
- Date : 2026-11-06
- Portée : Arch Linux, Ryoku sous Niri, PipeWire et EasyEffects ; test réalisé sur un Dell Latitude 7440.
- Environnements testés : EasyEffects 8.3.2, PipeWire 1.6.10, raccourcis Niri et barre Quickshell Ryoku.
- Configuration actuelle : EasyEffects reste installé et ses presets sont conservés, mais son démarrage automatique est désactivé. WirePlumber applique les traitements par smart filters, choisit automatiquement le sink physique de sortie et conserve « Audio interne Stéréo analogique » comme source d'entrée par défaut.
- Historique : les sections EasyEffects ci-dessous consignent l'ancienne correction du volume en mode sink virtuel ; l'essai natif est devenu la configuration actuelle.

## Symptôme historique en mode EasyEffects

Après avoir débranché les AirPods, WirePlumber remet bien le son sur les haut-parleurs, tandis qu'EasyEffects garde son sink virtuel comme sortie par défaut. Les touches qui appellent `wpctl` sur `@DEFAULT_AUDIO_SINK@` modifient alors le niveau d'`easyeffects_sink`, mais pas celui des haut-parleurs ni celui des AirPods.

## Diagnostic en mode EasyEffects

`wpctl status` montre les haut-parleurs ou les AirPods comme sink matériel et `easyeffects_sink` comme sortie par défaut. Pendant une lecture, `pw-link -l` montre que la sortie `ee_soe_output_level` d'EasyEffects est reliée au sink matériel actif. Le réglage de volume du sink virtuel ne remplace pas le contrôle de volume de ce périphérique matériel.

La sortie par défaut virtuelle est utile au traitement EasyEffects et à l'autoload des profils. La sélection directe d'un périphérique matériel contourne cette chaîne tant que le flux n'est pas redirigé vers le sink EasyEffects.

## Réglage du helper de volume

Un helper utilisateur `~/.local/bin/ryoku-audio-output` détermine la sortie cible dans cet ordre :

1. Pendant une lecture EasyEffects, il repère dans `pw-link -l` le sink relié à `ee_soe_output_level:output_FL`.
2. Si le défaut est l'entrée d'un smart filter WirePlumber (`effect_input.ryoku-*`), il suit le lien de sortie correspondant jusqu'au sink physique.
3. Sinon, il cible le sink physique renvoyé par `pactl get-default-sink`, qui suit la sortie sélectionnée par WirePlumber.
4. Si EasyEffects est relancé et garde `easyeffects_sink` comme défaut avant que sa chaîne de sortie soit liée, il utilise `outputDevice` dans `~/.config/easyeffects/db/easyeffectsrc` en secours.
5. Il résout le nom en identifiant PipeWire à partir de `wpctl status -n`, puis ajuste le volume ou la sourdine avec `wpctl`.

Un wrapper utilisateur `~/.local/bin/ryoku-volume` appelle ce helper pour les commandes `up` et `down`, avant `/usr/bin` dans le `PATH`. Les raccourcis Niri de hausse et de baisse appellent `ryoku-volume`; le raccourci de sourdine appelle `ryoku-audio-output mute`. Les deux fichiers de configuration à conserver sont `~/.config/niri/rebinds.kdl` et `~/.config/ryoku/user_edits/niri/rebinds.kdl`.

Comme le OSD Ryoku écoute normalement le volume du sink par défaut, le helper lui envoie le niveau matériel et l'état muet avec :

```bash
qs ipc --config shell call osd showVolume <pourcentage> <true-ou-false>
```

`OsdFeed.qml` et `OsdSource.qml` mémorisent brièvement cette valeur pour afficher le bon niveau et déclencher le cadre. Dans l'ancien mode EasyEffects, le sink virtuel restait actif et les règles d'autoload pour les haut-parleurs et les AirPods restaient inchangées.

### Barre QS après rechargement

Lors du rechargement de Quickshell nécessaire à l'OSD, le catalogue intégré de widgets QSbar n'était pas chargé avant la normalisation du layout : l'IPC ne retournait que `ryoku-pods` alors que `shell.json` conservait la disposition complète. Dans `~/.config/quickshell/shell/modules/bar/barstyles/qsbar/core/BarCatalog.qml`, le `DeferredFileView` du catalogue a été remplacé par un `FileView` bloquant le chargement et appelant `_load(text())` dans `onLoaded`. Après le rechargement, la disposition IPC complète est revenue.

## Validation de l'ancien mode EasyEffects

- `ryoku-volume up` a fait passer le volume matériel des haut-parleurs de 60 à 65 % ; `down` l'a ramené à 60 %.
- Deux bascules de sourdine ont rétabli l'état initial non muet. Pendant ces vérifications, `easyeffects_sink` est resté à 15 %.
- L'appel IPC de l'OSD a affiché la surface `ryoku-osd` et le pourcentage physique.
- Après le rechargement QSbar, `qs ipc --config shell call qsbar layout` a retourné les widgets gauche, centre et droite configurés dans `shell.json`.
- L'utilisateur a confirmé le retour du son et des commandes.

## Essai séparé de routage natif sans EasyEffects

Le 2026-11-06, EasyEffects a été arrêté temporairement pour vérifier la sélection native des sorties. Avec les AirPods portés, `wpctl status -n` montrait les haut-parleurs (sink 119) et les AirPods (sink 133), mais les haut-parleurs restaient la sortie par défaut. `priority.session` valait 1009 pour les haut-parleurs et 1010 pour les AirPods.

La section `Default Configured Devices` conservait une sélection de sortie `easyeffects_sink`, qui empêchait WirePlumber d'élire la sortie par priorité. `wpctl clear-default 0` a effacé la sélection mémorisée de sortie (sans toucher à la source par défaut) ; WirePlumber a alors choisi les AirPods. L'utilisateur a confirmé que la bascule entre AirPods portés et haut-parleurs se fait dans les deux sens. La sélection est automatique selon les sinks disponibles et leur priorité ; les applications dont le flux suit la sortie par défaut suivent ce changement.

Limite observée : lorsque l'utilisateur met ses AirPods, la sortie bascule correctement vers ceux-ci, mais la lecture en cours se met en pause au lieu de continuer sur les écouteurs. La cause n'est pas encore diagnostiquée et aucun correctif n'a été appliqué ; le routage de sortie fonctionne, mais la continuité de lecture reste à examiner.

EasyEffects était arrêté pendant cet essai : les fichiers de presets et d'autoload sont restés présents, mais aucun traitement EasyEffects n'était appliqué. Ensuite, des smart filters WirePlumber ont été créés dans `~/.config/wireplumber/wireplumber.conf.d/80-ryoku-audio-smart-filters.conf`, avec une chaîne de traitement propre aux haut-parleurs et une propre aux AirPods. Le sink matériel reste le défaut ; WirePlumber insère le filtre correspondant à sa cible. L'EQ a été transcrit en biquads PipeWire ; le compresseur multibande et le limiteur des haut-parleurs ont été remappés vers des plugins LV2 LSP. Les algorithmes de compresseur/limiteur et les coefficients biquad peuvent différer de ceux d'EasyEffects : le rendu doit être confirmé par écoute. Les presets EasyEffects source restent intacts.

Les filtres apparaissent dans `wpctl status` sous « Filters » avec des entrées `effect_input.*`. Ce sont les points d'entrée des traitements, pas des sorties matérielles supplémentaires. Il faut laisser le sink physique comme sortie par défaut pour que WirePlumber choisisse automatiquement les haut-parleurs ou les AirPods ; ne pas sélectionner manuellement ces filtres dans le sélecteur de sortie. Les descriptions sont préfixées par « Traitement interne automatique » pour les distinguer.

EasyEffects a été retiré du démarrage automatique pour que son sink ne reprenne pas la sortie par défaut à la prochaine session : `autostartOnLogin=false` et l'entrée est renommée `~/.config/autostart/com.github.wwmm.easyeffects.desktop.disabled`. Les fichiers sauvegardés avant ce changement sont dans `~/.config/easyeffects/backup-native-smart-filters-20261106-094614/`. Les smart filters sont chargés par WirePlumber ; un redémarrage complet de l'ordinateur n'est pas requis.

Le 2026-11-06, le helper de volume a été adapté au routage natif : sans liaison EasyEffects, il cible le sink physique par défaut au lieu du `outputDevice` EasyEffects mémorisé, qui pouvait rester sur les haut-parleurs. S'il détecte qu'un smart filter a été choisi comme défaut, il suit la sortie de ce filtre jusqu'au sink physique. Après qu'une sélection de filtre a perturbé les commandes, les entrées de sink sauvegardées dans `~/.local/state/wireplumber/default-nodes` ont été retirées en préservant les sélections de source ; une copie est conservée en `default-nodes.before-audio-default-clear-20261106`.

L'utilisateur a ensuite confirmé que le changement de sortie et le bouton de volume fonctionnent. `wpctl status` montrait les AirPods comme sink actif, les haut-parleurs internes disponibles et aucune sortie imposée dans `Default Configured Devices`.

À la demande de l'utilisateur, la source d'entrée par défaut est fixée sur `alsa_input.pci-0000_00_1f.3.analog-stereo`, affichée « Audio interne Stéréo analogique ». Le réglage a été appliqué avec `wpctl set-default` et vérifié dans `wpctl status` et via `pactl get-default-source`. Ce choix d'entrée est mémorisé séparément et ne modifie pas la sélection automatique de la sortie.

Le sélecteur audio peut afficher « Traitement interne automatique — haut-parleurs », « Traitement interne automatique — AirPods » et le sink matériel « Audio interne Stéréo analogique ». Les deux entrées « Traitement interne automatique » sont les smart filters `effect_input.*`, pas des sorties matérielles supplémentaires. Il faut les conserver pour garder les profils audio ; WirePlumber les applique automatiquement. Leur présence dans la liste ne signifie pas qu'elles sont la sortie physique active. Éviter de les choisir manuellement si l'on souhaite laisser WirePlumber décider entre les périphériques. L'utilisateur a confirmé le fonctionnement courant ; le cas de secours du helper après sélection manuelle d'un filtre n'a pas été vérifié séparément.

## Persistance et retour arrière

Le helper et son wrapper résident dans `~/.local/bin/`; les raccourcis source se trouvent dans les deux fichiers Niri indiqués plus haut. Les adaptations OSD et le chargement du catalogue QSbar résident dans `~/.config/quickshell/` et doivent être conservés si le shell est réinstallé ou réinitialisé.

Pour revenir à l'ancien ciblage, restaurer les fichiers Niri et Quickshell depuis une copie de configuration, puis retirer `~/.local/bin/ryoku-audio-output` et `~/.local/bin/ryoku-volume`. Cela rétablit les raccourcis qui ciblent le sink par défaut et supprime l'affichage OSD matériel.

## Références

- [Autoload EasyEffects par appareil](../../../../../../OUTILS/EASYEFFECTS/autoload-par-appareil.md) : profils séparés pour AirPods et haut-parleurs.
- [Preset Waves ON des haut-parleurs Dell](../../../02-SYSTEME/MACHINES/portable-dell/03-CONFIGURATION/easyeffects-modele-waves-on.md).
