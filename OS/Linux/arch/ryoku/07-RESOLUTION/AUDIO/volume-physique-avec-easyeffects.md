# Routage audio natif et volume matériel sous Ryoku

Résumé : WirePlumber choisit automatiquement entre les haut-parleurs et les AirPods. Pour les haut-parleurs internes, les touches, le panneau de volume, l’OSD et QSbar affichent ou règlent PCM ; les autres sorties restent pilotées par PipeWire. Les smart filters issus des presets EasyEffects restent à compléter et à valider par écoute.

- Statut : routage, filtres WirePlumber, remappage HDA au démarrage et lien de volume PipeWire/ALSA vérifiés le 2026-11-06 ; l'indicateur PCM QSbar et le curseur du panneau ont été confirmés par l'utilisateur le 2026-11-07. Le repli de l'OSD vers PCM est corrigé localement ; la vérification par l'utilisateur reste à faire. Le retour audible des haut-parleurs supérieurs après retask de `0x14` est confirmé par l'utilisateur. La conversion des presets reste incomplète.
- Date : 2026-11-07
- Portée : Arch Linux, Ryoku sous Niri, PipeWire et EasyEffects ; test réalisé sur un Dell Latitude 7440.
- Environnements testés : EasyEffects 8.3.2, PipeWire 1.6.10, raccourcis Niri et barre Quickshell Ryoku.
- Configuration actuelle : EasyEffects reste installé et ses presets sont conservés, mais son démarrage automatique est désactivé. Les smart filters WirePlumber sont actifs dans `~/.config/wireplumber/wireplumber.conf.d/80-ryoku-audio-smart-filters.conf` ; une copie `.conf.disabled` est conservée. La règle temporaire `soft-mixer` a été désactivée. Les raccourcis de volume pilotent désormais `PCM` sur la sortie analogique interne PCH ; ils gardent PipeWire pour les autres sorties. WirePlumber garde la sélection des sinks physiques et « Audio interne Stéréo analogique » comme source d'entrée par défaut.
- Historique : les sections EasyEffects ci-dessous consignent l'ancienne correction du volume en mode sink virtuel ; l'essai natif est devenu la configuration actuelle.

## Symptôme historique en mode EasyEffects

Après avoir débranché les AirPods, WirePlumber remet bien le son sur les haut-parleurs, tandis qu'EasyEffects garde son sink virtuel comme sortie par défaut. Les touches qui appellent `wpctl` sur `@DEFAULT_AUDIO_SINK@` modifient alors le niveau d'`easyeffects_sink`, mais pas celui des haut-parleurs ni celui des AirPods.

## Diagnostic en mode EasyEffects

`wpctl status` montre les haut-parleurs ou les AirPods comme sink matériel et `easyeffects_sink` comme sortie par défaut. Pendant une lecture, `pw-link -l` montre que la sortie `ee_soe_output_level` d'EasyEffects est reliée au sink matériel actif. Le réglage de volume du sink virtuel ne remplace pas le contrôle de volume de ce périphérique matériel.

La sortie par défaut virtuelle est utile au traitement EasyEffects et à l'autoload des profils. La sélection directe d'un périphérique matériel contourne cette chaîne tant que le flux n'est pas redirigé vers le sink EasyEffects.

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

### Barre QS après rechargement

Un essai a remplacé le `DeferredFileView` de `BarCatalog.qml` par un `FileView` bloquant ; il a modifié le rendu de QSbar et a été retiré le 2026-11-07. Le fichier actif est revenu à la version fournie par Ryoku. Si le catalogue est incomplet après un rechargement, réétudier la migration du layout avant de réappliquer ce changement.

### Indicateur de volume QSbar

Depuis le 2026-11-07, le chiffre du widget audio QSbar suit le niveau `PCM` ALSA lorsque le sink par défaut commence par `alsa_output.pci-0000_00_1f.3.`. Le singleton `PcmVolume.qml` relit `PCM` avec `amixer -c PCH sget PCM` chaque seconde, seulement lorsque cette sortie est active ; cette lecture ponctuelle évite de laisser un processus d'écoute ALSA après un rechargement Quickshell. Le nom de carte suit `RYOKU_PCM_CARD` si cette variable est définie, comme le helper des touches. Pour les autres sorties, le widget garde le volume PipeWire. La molette du widget appelle `ryoku-volume` sur la sortie interne ; le curseur et la molette du panneau de volume règlent aussi `PCM` en interne.

Les fichiers de cette adaptation sont `shell/audio/PcmVolume.qml`, `shell/audio/qmldir` et `shell/modules/bar/barstyles/qsbar/modules/AudioWidget.qml`, dans `~/.config/quickshell/` et `~/.config/ryoku/user_edits/quickshell/`. L'installateur audio conserve ces overlays dans `05-SCRIPT/AUDIO/`, les déploie dans `user_edits` et les applique aussi aux fichiers actifs.

Le panneau de volume ouvert par clic a ensuite été corrigé de la même façon : pour le sink analogique PCH, son curseur et sa molette écrivent `PCM` via `PcmVolume.setVolume()` et affichent le pourcentage PCM. Les autres sorties gardent le contrôle PipeWire. La sourdine reste celle du sink PipeWire ; le réglage PCM au-dessus de 100 % est désactivé pour les haut-parleurs internes. Fichiers actifs et overlays persistants : `shell/modules/bar/barstyles/qsbar/panels/VolumePanel.qml` et `shell/audio/PcmVolume.qml`. Après rechargement de Quickshell, l'utilisateur a confirmé que le résultat est correct (2026-11-07).

## Validation de l'ancien mode EasyEffects

- `ryoku-volume up` a fait passer le volume matériel des haut-parleurs de 60 à 65 % ; `down` l'a ramené à 60 %.
- Deux bascules de sourdine ont rétabli l'état initial non muet. Pendant ces vérifications, `easyeffects_sink` est resté à 15 %.
- L'appel IPC de l'OSD a affiché la surface `ryoku-osd` et le pourcentage physique.
- Après le rechargement QSbar, `qs ipc --config shell call qsbar layout` a retourné les widgets gauche, centre et droite configurés dans `shell.json`.
- L'utilisateur a confirmé le retour du son et des commandes.

## Essai séparé de routage natif sans EasyEffects

Le 2026-11-06, EasyEffects a été arrêté temporairement pour vérifier la sélection native des sorties. Avec les AirPods portés, `wpctl status -n` montrait les haut-parleurs (sink 119) et les AirPods (sink 133), mais les haut-parleurs restaient la sortie par défaut. `priority.session` valait 1009 pour les haut-parleurs et 1010 pour les AirPods.

La section `Default Configured Devices` conservait une sélection de sortie `easyeffects_sink`, qui empêchait WirePlumber d'élire la sortie par priorité. `wpctl clear-default 0` a effacé la sélection mémorisée de sortie (sans toucher à la source par défaut) ; WirePlumber a alors choisi les AirPods. L'utilisateur a confirmé que la bascule entre AirPods portés et haut-parleurs se fait dans les deux sens. La sélection est automatique selon les sinks disponibles et leur priorité ; les applications dont le flux suit la sortie par défaut suivent ce changement.

Pause à l'insertion : les journaux de LibrePods ont montré qu'il envoie une commande MPRIS `Pause` au lecteur actif lors d'un événement de détection d'oreille. En mode « One », retirer un seul écouteur suffit à déclencher la pause ; le mode « Both » correspond à `PauseWhenBothRemoved` et attend le retrait des deux. Il s'agit de la politique de détection de LibrePods, distincte du routage WirePlumber.

EasyEffects était arrêté pendant cet essai : les fichiers de presets et d'autoload sont restés présents, mais aucun traitement EasyEffects n'était appliqué. Ensuite, des smart filters WirePlumber ont été créés dans `~/.config/wireplumber/wireplumber.conf.d/80-ryoku-audio-smart-filters.conf`, avec une chaîne de traitement propre aux haut-parleurs et une propre aux AirPods. Le sink matériel reste le défaut ; WirePlumber insère le filtre correspondant à sa cible. L'EQ a été transcrit en biquads PipeWire ; le compresseur multibande et le limiteur des haut-parleurs ont été remappés vers des plugins LV2 LSP. Les algorithmes de compresseur/limiteur et les coefficients biquad peuvent différer de ceux d'EasyEffects : le rendu doit être confirmé par écoute. Les presets EasyEffects source restent intacts.

Les filtres apparaissent dans `wpctl status` sous « Filters » avec des entrées `effect_input.*`. Ce sont les points d'entrée des traitements, pas des sorties matérielles supplémentaires. Il faut laisser le sink physique comme sortie par défaut pour que WirePlumber choisisse automatiquement les haut-parleurs ou les AirPods ; ne pas sélectionner manuellement ces filtres dans le sélecteur de sortie. Les descriptions sont préfixées par « Traitement interne automatique » pour les distinguer.

EasyEffects a été retiré du démarrage automatique pour que son sink ne reprenne pas la sortie par défaut à la prochaine session : `autostartOnLogin=false` et l'entrée est renommée `~/.config/autostart/com.github.wwmm.easyeffects.desktop.disabled`. Les fichiers sauvegardés avant ce changement sont dans `~/.config/easyeffects/backup-native-smart-filters-20261106-094614/`. Les smart filters sont chargés par WirePlumber ; un redémarrage complet de l'ordinateur n'est pas requis.

Le 2026-11-06, le helper de volume a été adapté au routage natif : sans liaison EasyEffects, il cible le sink physique par défaut au lieu du `outputDevice` EasyEffects mémorisé, qui pouvait rester sur les haut-parleurs. S'il détecte qu'un smart filter a été choisi comme défaut, il suit la sortie de ce filtre jusqu'au sink physique. Après qu'une sélection de filtre a perturbé les commandes, les entrées de sink sauvegardées dans `~/.local/state/wireplumber/default-nodes` ont été retirées en préservant les sélections de source ; une copie est conservée en `default-nodes.before-audio-default-clear-20261106`.

L'utilisateur a ensuite confirmé que le changement de sortie et le bouton de volume fonctionnent. `wpctl status` montrait les AirPods comme sink actif, les haut-parleurs internes disponibles et aucune sortie imposée dans `Default Configured Devices`.

À la demande de l'utilisateur, la source d'entrée par défaut est fixée sur `alsa_input.pci-0000_00_1f.3.analog-stereo`, affichée « Audio interne Stéréo analogique ». Le réglage a été appliqué avec `wpctl set-default` et vérifié dans `wpctl status` et via `pactl get-default-source`. Ce choix d'entrée est mémorisé séparément et ne modifie pas la sélection automatique de la sortie.

Quand les smart filters sont actifs, le sélecteur audio peut afficher « Traitement interne automatique — haut-parleurs » et « Traitement interne automatique — AirPods ». Ce sont les entrées `effect_input.*` des traitements, pas des sorties matérielles. Leur présence ne signifie pas qu'elles sont la sortie physique active. Éviter de les choisir manuellement si l'on souhaite laisser WirePlumber décider entre les périphériques.

## Diagnostic du rendu et désactivation temporaire des filtres

Le 2026-11-06, l'utilisateur a signalé un son grésillant sur les AirPods, puis un rendu étrange aussi sur les haut-parleurs après l'installation des smart filters. Pendant la lecture dans Microsoft Edge, `pw-link -l` a confirmé que le flux passait par `effect_input.ryoku-speakers-smartfx` avant de rejoindre le sink physique.

La comparaison avec les presets EasyEffects a révélé que la conversion vers PipeWire était incomplète : les bandes d'EQ des AirPods correspondaient, mais le pré-gain `-2.5 dB` du preset n'avait pas été transcrit. Pour les haut-parleurs, les deux étages `stereo_tools` n'étaient pas présents et le compresseur multibande et le limiteur avaient été remplacés par des plugins LSP différents. Le preset source des haut-parleurs indique `0 dB` de gain d'entrée ; les différences de traitement restent donc un point important à corriger et valider par écoute.

Les smart filters ont été désactivés en renommant leur fichier de configuration en `.conf.disabled`, puis en redémarrant WirePlumber. Après ce changement, `wpctl status` montrait le sink physique des haut-parleurs par défaut, le micro interne toujours sélectionné et aucun filtre de traitement chargé. Le routage natif reste configuré, mais la bascule après cette désactivation et le retour du rendu normal doivent être confirmés par l'utilisateur. Les AirPods étaient encore connectés en Bluetooth, mais leur profil audio PipeWire était `off` après une erreur de transport Bluetooth ; le son des AirPods n'a donc pas été revalidé.

## Dell Latitude 7440 : haut-parleurs supérieurs et volume

Le codec Realtek ALC289 a un connecteur interne inutilisé sur la broche HDA `0x14` à l'initialisation (`0x411111f0`). Dans `hdajackretask`, la broche `0x14` a été configurée comme « Internal speaker » (`0x90170150`) et un boot override a été enregistré. Après le redémarrage du 2026-11-06, `journalctl -b -k` confirme `Applying patch firmware 'hda-jack-retask.fw'` et l'auto-configuration HDA signale deux sorties haut-parleur (`0x17` et `0x14`). Le `Pin Default` de `/proc/asound/card0/codec#0` reste à la valeur BIOS `0x411111f0` ; il ne faut pas l'utiliser seul pour conclure que le patch n'a pas été chargé. La broche `0x17` est une sortie interne « Speaker » (`0x90170110`) dont la connexion de convertisseur active est `0x06`.

Le 2026-11-06, l'utilisateur a installé le boot override. `hdajackretask` a créé `/etc/modprobe.d/hda-jack-retask.conf` et `/lib/firmware/hda-jack-retask.fw`, qui contient `0x14 0x90170150`. Le remappage doit donc être réappliqué au chargement du codec après redémarrage.

Le 2026-11-06, le fichier WirePlumber des smart filters a été réactivé sans démarrer EasyEffects. Pendant la lecture dans Microsoft Edge, `pw-link -l` confirme le chemin `Microsoft Edge -> effect_input.ryoku-speakers-smartfx -> effect_output.ryoku-speakers-smartfx -> alsa_output.pci-0000_00_1f.3.analog-stereo`. Le sink actif est `analog-output-speaker`.

Le contrôle `Master` ne publie pas d'échelle en décibels. Une règle `soft-mixer` a été essayée puis désactivée, car elle séparait la valeur PipeWire de la barre `Master` dans ALSA. La règle `api.alsa.disable-mixer-path = true` est toujours active dans `~/.config/wireplumber/wireplumber.conf.d/82-ryoku-alc289-keep-headphone-path.conf`. Une hypothèse antérieure voulait que `Headphone` pilote également les haut-parleurs supérieurs, en s'appuyant sur un rapport concernant le même modèle ; les essais actuels de l'utilisateur la contredisent : `Headphone` à 100 % ne change pas le son entendu.

Le dump du codec associe les contrôles à des éléments distincts : `Bass Speaker Playback Volume` règle l'ampli de sortie du convertisseur HDA `0x02`, tandis que `Bass Speaker Playback Switch` commande l'ampli de la broche `0x14` ; `Speaker Playback Switch` commande la broche `0x17`. `Headphone Playback Volume` règle le convertisseur `0x03`, et `Headphone Playback Switch` est sur la broche casque `0x21`. Ces noms ne prouvent donc pas à eux seuls quels transducteurs physiques reçoivent le signal.

Essais communiqués le 2026-11-06 : avec `Master` à 0 %, `PCM` à 100 %, `Bass Speaker` à 100 % et `Headphone` à 100 %, l'utilisateur n'entend que les haut-parleurs du bas. Le curseur `Bass Speaker` n'a pas d'effet audible, mais son interrupteur doit rester sur `ON` ; le passer sur `MM` coupe tout son. `Headphone` n'a pas d'effet audible. L'utilisateur identifie alors empiriquement `PCM` comme le réglage de volume des haut-parleurs du bas. Ces attributions par haut-parleur sont des observations préliminaires, révisées après les essais ultérieurs décrits plus bas. Le rapport `diagnostic-20261106-164449.txt` montre au moment de sa capture `PCM` 100 %, `Bass Speaker` 0 % et ON, `Headphone` 0 % et ON, `Master` 0 % et ON, mais aussi une sortie PipeWire à 0 % et aucun flux actif. L'écoute rapportée et le snapshot ne sont donc pas une mesure simultanée du niveau PipeWire.

Le boot override (`/lib/firmware/hda-jack-retask.fw` et `/etc/modprobe.d/hda-jack-retask.conf`) demande `0x14 0x90170150` et le journal du démarrage confirme qu'il a été chargé. Le noyau précise que `user_pin_configs` est pris en compte à la prochaine reconfiguration du codec, et que le fichier de patch peut être chargé avant l'initialisation ([documentation HD-Audio du noyau](https://docs.kernel.org/sound/hd-audio/notes.html)). L'essai à chaud avait échoué avec « Device or resource busy » ; le patch au démarrage est donc la voie validée actuellement.

Validation à bas niveau le 2026-11-06 : de 0 %, `ryoku-audio-output up` a passé le sink logiciel à 5 % (PipeWire affiche `-80,27 dB`), puis `down` l'a remis à 0 %. Pendant cet essai, `Master` est resté à 68 % et `Bass Speaker` à 70 %. Les essais à des niveaux intermédiaires et la confirmation auditive restent à faire.

### Outil de diagnostic interactif

`~/.local/bin/ryoku-audio-lab` est un TUI Python sans dépendance supplémentaire. Le lancer depuis un terminal de la session graphique pour conserver l'accès à `hdajackretask`. Les onglets affichent l'état PipeWire/ALSA, permettent de régler les contrôles ALSA et le volume PipeWire, de sélectionner une sortie matérielle, d'inspecter les configurations de broches et d'ouvrir `hdajackretask`, ainsi que de consulter/redémarrer les services utilisateur ou basculer les smart filters. `T` joue un court test gauche/droite/stéréo directement sur la sortie physique par défaut, donc sans valider le chemin EasyEffects ; `S` écrit un diagnostic local dans `~/.local/state/ryoku-audio-lab/`. Le rapport peut être produit sans interface avec `ryoku-audio-lab --report`.

Touches : `1` à `5` changent d'onglet, `↑`/`↓` sélectionnent un contrôle ou une sortie, `←`/`→` règlent le contrôle ALSA sélectionné par pas de 5 %, `M` commute son interrupteur, `+`/`-` règlent le volume PipeWire, `T` joue le test, `S` enregistre le rapport, `H` ouvre `hdajackretask`, `W`/`P` redémarrent WirePlumber/PipeWire et `F` active ou désactive les smart filters. Le réglage d'une broche reste effectué dans `hdajackretask`, et le changement de sortie par défaut, les commandes du mixeur et les redémarrages agissent immédiatement sur la session.

Premier relevé interactif communiqué par l'utilisateur : `Master` 0 % activé, `Speaker` activé sans curseur de volume, `Bass Speaker` 0 % activé, `Headphone` 0 % muet, `PCM` 100 %. Les touches de volume changent `Master`. Cela confirme le contrôle visé par les touches, mais pas que `Master` règle globalement toutes les sorties. Ne pas supposer que `Speaker` regroupe `Bass Speaker` et `Headphone` sans essai.

Les rapports précédents affichaient `user_pin_configs` comme la configuration « active » et le TUI a ensuite, à tort, traité le `Pin Default` de `/proc` comme la configuration chargée. Il distingue maintenant la configuration suivant la priorité user/driver/BIOS, la valeur `Pin Default` du fichier proc, l'override de démarrage et la présence du chargement dans le journal noyau. Il affiche également l'échelle en dB quand ALSA la publie. Son test tonal ne démarre pas si la sortie PipeWire est muette ou à 0 %.

Après le redémarrage, l'utilisateur a relevé dans le TUI `Master` 5 %, `Bass Speaker` 5 % (−62,25 dB), `Headphone` 5 % (−62,25 dB), `PCM` 100 % et volume PipeWire 0 %. Le test tonal a donc été refusé et n'a produit aucun son de test. Le journal noyau du démarrage confirme par ailleurs que le firmware de retask a été appliqué et que le parseur détecte les sorties `0x17` et `0x14`. Le test tonal a été relevé à un niveau modéré, toujours limité par le volume global PipeWire.

Le rapport `diagnostic-20261106-170526.txt` montre que le sink physique était en réalité à 100 % (`wpctl status` indique `[vol: 1.00]` et `wpctl get-volume 120` renvoie `1.00`), malgré le champ PipeWire à 0 % du TUI. `sink_id()` ne reconnaissait pas l'en-tête `├─ Sinks:` décoré de l'arborescence `wpctl` et renvoyait une valeur vide, interprétée comme 0 %. Ce parseur a été corrigé et vérifié : il retrouve l'ID 120 et 100 %. Au même moment, Plex était connecté au sink EasyEffects ; le test `T` cible volontairement le sink matériel physique pour isoler les haut-parleurs.

Essais ultérieurs communiqués par l'utilisateur : son essai antérieur le plus contrôlé consistait à changer uniquement le curseur ALSA `Headphone`, les autres niveaux restant fixes ; le son des haut-parleurs supérieurs changeait, et le mettre à zéro modifiait également le son. C'est l'indice empirique principal pour associer le curseur `Headphone` aux haut-parleurs supérieurs. `PCM` à 0 % laisse le flux de test démarrer mais le rend inaudible, ce qui confirme le rôle du gain PCM. Quand `Master` et `Bass Speaker` sont coupés, le TUI refuse le test faute de sortie audible. Réglages montrés ensuite : `Master`, `Bass Speaker`, `Headphone`, `PCM` à 100 %, `Speaker` ON ; le champ PipeWire restait erronément à 0 % dans l'ancienne version. Le test TUI utilise maintenant 1 kHz à gauche, 2 kHz à droite, puis stéréo à 1 kHz ; il prévient si les interrupteurs `Master`/`Bass Speaker` sont coupés ou si le gain PCM est inférieur à −40 dB.

Dernier essai communiqué : l'utilisateur rapporte que `Headphone` ON/MM n'a pas changé le son. Cependant, sur la capture associée, `Speaker` était sur MM et le TUI a refusé le test car PipeWire était muet ; cette comparaison ne dit donc rien sur l'effet de l'interrupteur Headphone. Ne pas en déduire que son curseur de volume n'agit pas sur les haut-parleurs supérieurs. Réactiver `Speaker` avant tout nouveau test TUI ; ne pas refaire l'essai d'isolation `Speaker` tant que sa coupure provoque le muet global PipeWire.

Rollback de contrôle le 2026-11-06 : après avoir temporairement désactivé `82-ryoku-alc289-keep-headphone-path.conf` puis redémarré WirePlumber, le système a ramené `Headphone` à 0 % (−65,25 dB) et OFF. Cette règle a été réactivée ; après un nouveau redémarrage de WirePlumber, `Headphone` a été remis à 70 % (−19,50 dB), ON. Cette observation confirme que la sélection de chemin WirePlumber peut écraser l'état du contrôle Headphone ; garder la règle active pendant les essais.

Après restauration de la règle, l'utilisateur trouve le son meilleur sans pouvoir le confirmer avec certitude. Il a comparé l'interrupteur Headphone ON/MM et n'a pas entendu de différence. L'état ALSA relu ensuite est `Headphone` 70 % (−19,50 dB), interrupteur OFF, règle WirePlumber active. Le TUI envoie son test directement au sink matériel, alors que Plex est routé vers EasyEffects ; ce test ne reproduit donc pas le chemin de lecture habituel. La consigne précédente de comparer le curseur tout en laissant `Headphone` sur OFF était incorrecte. Pour reprendre l'essai contrôlé initial, conserver le même audio habituel, mettre le commutateur `Headphone` sur ON et le laisser ainsi, puis comparer uniquement son curseur à 0 % et 70 % en gardant les autres contrôles fixes.

### Mise à jour après réinstallation de l'override `0x14`

Après suppression de l'override et redémarrage, `0x14` était revenu à la valeur BIOS `0x411111f0` et seul le bas était audible ; le curseur `Speaker` modifiait cette sortie. L'utilisateur a ensuite réinstallé dans `hdajackretask` l'override de démarrage `0x14 0x90170150` (« Internal speaker »), puis redémarré. Au démarrage suivant, le journal noyau confirmait `Applying patch firmware 'hda-jack-retask.fw'`, `user_pin_configs` contenait `0x14 0x90170150`, et l'auto-configuration ALC289 annonçait les sorties haut-parleur `0x17` et `0x14`. La valeur BIOS initiale `0x411111f0` reste dans `init_pin_configs` et le champ `Pin Default` du codec ; ces champs décrivent l'état initial et ne contredisent pas le patch chargé.

Après ce redémarrage, le relevé ALSA était : `Master` 100 % ON, `Speaker` interrupteur ON sans curseur de volume, `Bass Speaker` 100 % ON, `Headphone` 0 % OFF et `PCM` 100 %. Le contrôle `Bass Speaker Playback Switch` est associé à la broche `0x14`, et `Speaker Playback Switch` à la broche `0x17`. En lecture Plex, passer l'interrupteur `Bass Speaker` sur MM a coupé tout le son ; il a été remis sur ON. Un essai antérieur du curseur `Bass Speaker` avait été perçu comme un changement de timbre. Les tests plus récents ci-dessous ne confirment pas que `Bass Speaker` commande un groupe physique distinct de `Master`.

Correction des essais précédents, communiquée par l'utilisateur le 2026-11-07 : `Master` et `Bass Speaker` semblent agir ensemble sur le même ensemble de haut-parleurs. Mettre l'un ou l'autre à 0 % donne, selon son écoute, un rendu strictement identique. Il estime que les deux curseurs doivent rester autour de 80–85 % au minimum pour que leurs changements aient un effet audible ; sous ce niveau, leurs variations ne changent plus le rendu à l'oreille, quel que soit le niveau de l'autre curseur. Cela remplace les anciennes attributions distinctes aux haut-parleurs du haut et du bas. Le constat reste empirique et ne démontre pas à lui seul le rôle électrique précis des contrôles ALSA. Le réglage de référence reste de laisser les interrupteurs `Speaker` et `Bass Speaker` sur ON, de garder `Master` et `Bass Speaker` au-dessus du seuil audible constaté, puis d'utiliser `PCM` pour régler le niveau d'écoute.

Les filtres réactivés sont une traduction des presets EasyEffects : ils ne reproduisent pas encore intégralement les plugins source, notamment les étages `stereo_tools` et les choix compresseur/limiteur déjà relevés ci-dessus. Si les artefacts sonores réapparaissent, terminer la conversion avant de considérer le rendu comme équivalent.

## Persistance et retour arrière

Le helper et son wrapper résident dans `~/.local/bin/`; les raccourcis source se trouvent dans les deux fichiers Niri indiqués plus haut. Les adaptations OSD et l'indicateur PCM QSbar résident dans `~/.config/quickshell/` et `~/.config/ryoku/user_edits/quickshell/`, et doivent être conservés si le shell est réinstallé ou réinitialisé.

Pour revenir à l'ancien ciblage, restaurer les fichiers Niri et Quickshell depuis une copie de configuration, puis retirer `~/.local/bin/ryoku-audio-output` et `~/.local/bin/ryoku-volume`. Cela rétablit les raccourcis qui ciblent le sink par défaut et supprime l'affichage OSD matériel.

## Réinstallation du trajet audio

L'installateur documenté dans [Scripts Ryoku — Audio](../../05-SCRIPT/AUDIO/README.md) regroupe les réglages validés pour le Latitude 7440 : packages PipeWire et LV2, filtres WirePlumber pour les haut-parleurs/AirPods, raccourcis PCM, état ALSA `Speaker`/`Master`/`Bass Speaker` et override HDA de la broche `0x14`. Il sauvegarde les fichiers remplacés et laisse le niveau PCM courant inchangé. Le script est rédigé d'après la configuration de cette machine ; sa fiche précise qu'il reste à valider sur une installation vierge.

## Références

- [Autoload EasyEffects par appareil](../../../../../../OUTILS/EASYEFFECTS/autoload-par-appareil.md) : profils séparés pour AirPods et haut-parleurs.
- [Preset Waves ON des haut-parleurs Dell](../../../02-SYSTEME/MACHINES/portable-dell/03-CONFIGURATION/easyeffects-modele-waves-on.md).
