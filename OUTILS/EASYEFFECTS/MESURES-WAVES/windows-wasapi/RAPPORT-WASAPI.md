# Essais Windows — Waves MaxxAudio / Latitude 7440

- Résumé : rapport de la première campagne loopback WASAPI : Waves ON et OFF, répétabilité et dynamique.
- Statut : testé (mesures réalisées sous Windows, profils non validés à l'écoute)
- Date : 2026-11-05

Les dix captures numériques réalisées montrent un effet Waves mesurable et reproductible dans le loopback Realtek : correction fréquentielle importante, transferts entre canaux et comportement dépendant du niveau dans le grave. Le premier candidat SST ne décrit donc pas à lui seul le traitement observé. Ces mesures constituent une référence numérique exploitable pour la suite sous Linux ; elles ne mesurent pas le son acoustique des haut-parleurs.

## Conditions et acquisition

Acquisition le 29 octobre 2026 ; horodatages détaillés dans `manifest.json` (horloge Windows de cette session). Windows 11 Professionnel build 26300, Realtek 6.0.9954.2, Waves APO 12.2.0.18243, application MaxxAudio 2.0.54.0. Le périphérique de rendu est `Haut-parleur (Realtek(R) Audio)`, identifiant `{0.0.0.00000000}.{GUID-DU-PERIPHERIQUE}`. L'interface Waves indique **Haut-parleurs internes**, préréglage **Par défaut**, profil EQ **Réinitialisation complète**, courbe graphique plate. MaxxBass, Détails et Largeur sont restés à leur position initiale ; Minuit est resté désactivé.

Le format partagé a été interrogé directement par `IAudioClient::GetMixFormat` : WAVEFORMATEXTENSIBLE, **48000 Hz, deux canaux FL/FR, float32** (`mix-format.json`). Lecture et capture utilisent PyAudioWPatch/WASAPI en mode partagé, sur la sortie Realtek et son analogue loopback. Aucun câble virtuel, Stereo Mix, mode exclusif, flux RAW, microphone physique ou microphone virtuel n'a été utilisé. Les autres sessions audio étaient inactives à chaque lancement vérifié. Les captures restent un mélange système : une notification imprévue n'est pas exclue par construction, mais aucun incident de ce type n'a été identifié.

Le seul réglage Waves modifié est l'interrupteur **Playback Power**, via son contrôle dans l'application. Son état a été confirmé visuellement en bleu (ON) ou gris (OFF), avec captures de la fenêtre et inventaires UI. Chaque acquisition ouvre de nouveaux flux avec le même lecteur et le même fichier source dans chaque paire. OFF signifie cet interrupteur désactivé, **pas un bypass démontré de tout le traitement Dell/Realtek**. Le mode spatial propre à Windows n'a pas été confirmé indépendamment et n'a pas été modifié ; cela limite la description absolue de l'état initial.

Deux signaux de référence, WAV float32 sans normalisation, ont été utilisés :

- `reference/pilot.wav` : 15,75 s, silence, repère, balayages 80–18000 Hz gauche seule/droite seule, bruit à graine fixe 7440 et tonalités 997 Hz de -48 à -30 dBFS crête.
- `reference/dynamics.wav` : 26,75 s, tonalités mono corrélées 125 Hz puis 997 Hz, niveaux -30, -48, -36, -30 dBFS crête, silences entre segments. Le retour au même niveau permet de vérifier la dépendance à l'historique.

Toutes les sources ont une crête maximale de **-30 dBFS**. Les premiers essais ont utilisé un volume Windows de 10 %, puis 5 %. Après avoir vérifié que le mode muet laisse le signal accessible au loopback, les essais de dynamique ont été réalisés avec la sortie physique muette, à réglages identiques pour ON et OFF. Le volume et le mute d'origine ont été restaurés après chaque acquisition.

## Résultats

### Qualité et répétabilité

Les dix WAV sont stéréo float32 à 48 kHz, avec des valeurs finies, aucun échantillon à amplitude >=1, et aucun incident de callback PortAudio signalé. Cela ne constitue pas une preuve exhaustive d'absence de toute anomalie audio. Les empreintes SHA-256 des sources et captures ont été revérifiées. Les marges silencieuses permettent l'alignement malgré les premiers/derniers paquets partiels ; les séquences utiles sont couvertes.

Sur les pilotes, la différence de niveau RMS global entre deux répétitions OFF est d'environ **0,006 dB** ; entre les deux répétitions ON, **0,260 dB**. Les plateaux de tonalités sont beaucoup plus reproductibles : les gains calculés des deux séquences `dynamics-on1` et `dynamics-on2` sont identiques à la précision du calcul enregistré. Une faible différence sur un balayage ne doit donc pas être assimilée automatiquement à une nouvelle fonction Waves.

À source identique, ON augmente le RMS global du pilote d'environ **15,2 à 15,4 dB** par rapport à OFF. Ce chiffre dépend fortement du contenu du signal et ne représente pas un gain uniforme à appliquer à Linux. Les crêtes capturées vont jusqu'à environ -8,04 dBFS sur les essais de dynamique ON, sans écrêtage d'échantillons.

`analysis/aligned/` contient aussi des copies alignées ON/OFF et une copie ON atténuée par un facteur unique pour égaler le RMS de OFF sur les segments de source actifs. Cette comparaison préserve les rapports entre canaux ; elle égalise le RMS, pas la sonie perceptive. Les originaux restent intacts. Les projections scalaires et résidus de `summary.json` ne sont pas des gains de filtre ou des taux de distorsion : une différence de phase ou de retard peut suffire à rendre un résidu important.

### Fréquences et stéréo

`analysis/apparent-transfers.csv` contient les quatre transferts apparents L→L, L→R, R→L et R→R. Les estimations viennent des balayages séparés, avec moyennes d'énergie sur 1/12 d'octave. Elles caractérisent ces essais et ce niveau, pas un système linéaire prouvé.

Quelques valeurs sur le pilote ON n°1 et OFF n°1, en dB de gain par rapport au canal source :

| Fréquence | OFF L→L | ON L→L | ON L→R |
| --- | ---: | ---: | ---: |
| 100 Hz | -9,99 | +12,69 | +12,31 |
| 400 Hz | -7,12 | -2,52 | -12,43 |
| 800 Hz | -2,08 | +2,28 | -3,27 |
| 1600 Hz | -2,15 | +8,23 | +3,15 |
| 6400 Hz | -2,83 | +9,95 | -3,15 |

OFF, le canal opposé du balayage est numériquement nul dans ces captures. Le CSV le représente par un plancher de calcul à -600 dB : **ce n'est pas une mesure de bruit à -600 dB**. ON, un signal net apparaît sur le canal opposé, avec un comportement globalement similaire quand on inverse gauche et droite. Cela établit un traitement intercanal ; le qualifier précisément de virtualisation, crossfeed, élargissement ou combinaison demande une analyse de phase supplémentaire et une écoute. Les phases exportées sont relatives à l'alignement choisi, pas des délais acoustiques absolus.

Le gain propre à OFF varie aussi avec la fréquence. Il ne faut pas soustraire arbitrairement tout ce comportement en supposant que le rendu Linux brut lui est identique.

### Dépendance au niveau et harmoniques

Gains de la fondamentale, canal L, vers la fin des tonalités **mono corrélées** à 125 Hz :

| Source, dBFS crête | Gain OFF | Gain ON | Fondamentale ON, dBFS crête |
| --- | ---: | ---: | ---: |
| -48 | -6,245 dB | +28,550 dB | -19,450 |
| -36 | -6,245 dB | +23,528 dB | -12,472 |
| -30 | -6,245 dB | +20,762 dB | -9,238 |

Entre -48 et -30 dBFS en entrée, la fondamentale ON augmente donc d'environ 10,21 dB pour 18 dB d'augmentation de source. C'est compatible avec une compression du grave ; la pente équivalente sur cet intervalle correspond à environ **1,76:1**, sans identifier pour autant un compresseur interne, son seuil, sa structure ou son ratio universel. Ces chiffres incluent le traitement stéréo d'une source mono et ne sont pas directement ceux d'une bande EQ.

À 997 Hz, OFF donne -3,015 dB de gain ; ON donne environ +0,835 dB à -48 dBFS, +1,397 dB à -36 dBFS et +1,337 dB à -30 dBFS. Un traitement large bande unique ne décrit donc pas toute la réponse observée.

Un ajustement simultané des sinus/cosinus de la fondamentale et des harmoniques 2 à 8 évite la confusion avec la fuite d'une FFT à bins fixes. À 125 Hz et -30 dBFS, le rapport des harmoniques 2–8 à la fondamentale est proche de **-50 dB** ON, contre environ -107 dB OFF. À 997 Hz, ce rapport reste beaucoup plus faible, autour de -96 dB ON à -30 dBFS. Ce sont des mesures numériques dans cette capture, pas un THD acoustique étalonné ni une identification certaine de MaxxBass. Les fenêtres d'analyse commencent à 100 ms : elles ne permettent pas de déduire précisément attaque et relâchement.

### Volume et mute

Passer de 10 % à 5 % modifie le volume endpoint de -33,24 à -42,03 dB environ, sans atténuation correspondante de ce loopback : OFF, le RMS diffère de seulement 0,004 dB ; ON, l'écart reste comparable à la variabilité des répétitions. Le mute conserve également le signal numérique ON. **Dans cette configuration testée**, le signal capturé précède donc au moins cette atténuation/mise en sourdine physique. Cela ne prouve pas sa position par rapport à tous les APO, au DSP ou à l'amplificateur.

## Fichiers et reproduction

- `manifest.json` : métadonnées consolidées, identifiants, niveaux, états, sources, empreintes, preuves UI et restauration.
- `captures/` : dix captures brutes, non normalisées, avec fichiers JSON par acquisition.
- `reference/` : sources et description exacte des segments.
- `analysis/summary.json`, `segments.csv`, `apparent-transfers.csv`, `dynamics.json` : calculs et résultats.
- `analysis/resultats.png` et `resultats.pdf` : courbes de fréquence/stéréo et de niveau.
- `inventory-initial.json`, `windows-versions.json`, `mix-format.json`, `endpoint*.json`, exports du registre et captures UI : état et contexte.
- `wasapi_trials.py`, `dynamics_trials.py`, `analyze_trials.py`, `plot_results.py`, `finalize_trials.py`, `waves-ui.ps1` : outils reproductibles.
- `tools/python/` : Python embarqué local 3.13.9 provenant de python.org ; dépendances PyPI dans `requirements-lock.txt`. Ce runtime volumineux est exclu du ZIP de transfert.

Sous Windows, utiliser `tools\python\python.exe`. Commandes d'analyse sans acquisition : `analyze_trials.py`, `dynamics_trials.py`, puis `plot_results.py`. Pour rejouer une acquisition, consulter `wasapi_trials.py --help`, choisir un nouveau label et confirmer l'état dans Waves ; l'option `--muted` reste recommandée pour les mesures numériques dans cette configuration. Ne pas relancer `inventory` avant d'avoir archivé son résultat initial. Le script `waves-ui.ps1` photographie la fenêtre Waves ; `-TogglePlayback` clique sur le bouton de lecture et doit toujours être suivi d'une vérification visuelle de l'état. Un changement de disposition de l'application peut rendre cette automatisation inadaptée.

## Restauration et limites pour Linux

Waves Playback est revenu sur **ON** ; les boutons MaxxBass/Détails/Largeur, l'EQ et les préréglages n'ont pas été modifiés. Volume initial restauré exactement à l'arrondi API près : `0,3602023124694824`, mute `0`. Endpoint inchangé. Les contrôles sont consignés dans `restoration.json`. Aucun pilote/service ni protection d'amplificateur n'a été désactivé ou modifié. Le profil Linux existant est préservé.

La prochaine étape est de construire sous Linux une approximation **stéréo et dépendante du niveau**, en s'appuyant sur ces mesures plutôt que sur la banque SST seule. Ne pas appliquer directement les gains élevés du grave dans un égaliseur : ils font partie d'un traitement global avec compression et mélange entre canaux. Il faut vérifier le routage et les protections matérielles sous Linux, réserver de la marge et comparer des références à volume perçu comparable.

Les fonctions individuelles n'ont pas été isolées : les contrôles personnalisés ne donnent pas de valeur numérique accessible permettant ici une modification et une restauration exactes des boutons rotatifs. L'état d'usage complet a donc été conservé. Les quatre haut-parleurs physiques, leur amplification et les traitements situés après le loopback restent non mesurés. Une mesure acoustique avec accord et protocole séparés demeure nécessaire pour revendiquer une fidélité au son entendu sous Windows. Aucun nouveau noyau de convolution prétendument « exact » n'a été produit à partir de cette chaîne non linéaire.

## Documentation consultée

- [Microsoft : loopback WASAPI](https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording) — capture du mélange d'un endpoint de rendu.
- [Microsoft : architecture des APO](https://learn.microsoft.com/windows-hardware/drivers/audio/audio-processing-object-architecture) — traitements SFX/MFX/EFX à différents emplacements.
- [PyAudioWPatch, documentation du projet](https://github.com/s0d3s/PyAudioWPatch) — sélection explicite de l'analogue loopback WASAPI.
- [Pycaw, API](https://andremiras.github.io/pycaw/api/index.html) — accès aux endpoints, sessions et volumes.

Tous les fichiers et captures restent locaux ; aucun contenu audio ni export du registre n'a été envoyé à un service externe.
