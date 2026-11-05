# Mesures des effets Waves isolés — Latitude 7440

- Résumé : résultats de la campagne MaxxBass, Détails et Largeur isolés, avec leurs limites.
- Statut : testé (mesures réalisées sous Windows, profils non validés à l'écoute)
- Date : 2026-11-05

**36 captures WASAPI ont été réalisées et vérifiées.** La première a bien MaxxBass, Détails et Largeur tous à 0 %. Les trois effets ont ensuite été testés séparément à 25, 50, 75 et 100 %, avec les deux autres à zéro. Chaque fichier contient trois niveaux numériques : -60, -48 et -36 dBFS crête. À 50 % d’effet, le volume Windows a été testé à 5, 10, 15, 50 et 100 %.

Toutes les acquisitions sont réalisées avec la sortie physique muette, sur le même loopback Realtek partagé, stéréo float32 à 48 kHz. Aucun microphone ni essai acoustique à fort volume. Les volumes élevés ont été appliqués uniquement après confirmation du mute ; le volume initial est restauré avant de rétablir son état. Les détails, signaux et limites méthodologiques sont dans [METHODE.md](METHODE.md).

Les valeurs exactes des boutons sont maintenant lues via UI Automation **ItemStatus**, puis vérifiées avant et après chaque capture. Cela corrige la limitation de la première campagne, où cette propriété n’avait pas été relevée. Les captures brutes, états et empreintes sont dans `manifest.json`, `captures/` et `states/`.

## MaxxBass : grave, harmoniques et mélange entre canaux

Ce contrôle ne se résume pas à une bande d’égaliseur. Il renforce fortement le grave, avec une progression non proportionnelle au pourcentage, un gain dépendant du niveau et des harmoniques nettement mesurables sur les basses fréquences. Les valeurs ci-dessous concernent une source mono à -36 dBFS crête, canal L, fenêtre 300–500 ms ; les gains sont des **incréments par rapport aux trois boutons à zéro**, Playback restant ON.

| MaxxBass | Incrément à 80 Hz | Incrément à 125 Hz | Harmoniques 2–8 / fondamentale, à 80 Hz |
| ---: | ---: | ---: | ---: |
| 0 % | 0,00 dB | 0,00 dB | -88,81 dB |
| 25 % | 12,31 dB | 14,32 dB | -31,63 dB |
| 50 % | 18,63 dB | 19,83 dB | -29,66 dB |
| 75 % | 19,89 dB | 21,91 dB | -28,68 dB |
| 100 % | 20,14 dB | 22,57 dB | -28,44 dB |

Autre résultat important : avec **MaxxBass seul à 50 %**, une excitation gauche seule dans la bande proche de 125 Hz produit un signal sur la droite presque au même niveau et en phase. Le rapport opposé/direct est proche de +0,09 dB, phase -1,9°, au niveau source -48 dBFS. Ce comportement apparaît avec Largeur à zéro : tout transfert entre canaux ne doit donc pas être attribué à Largeur. Une extraction/réinjection de grave commun aux deux canaux est une piste de modèle, pas une identification du code Waves.

## Détails : renforcement fréquentiel et dépendance au niveau

Détails renforce davantage le haut du spectre, mais agit aussi autour de 1 kHz. Conditions identiques au tableau précédent.

| Détails | Incrément à 997 Hz | Incrément à 6000 Hz |
| ---: | ---: | ---: |
| 0 % | 0,00 dB | 0,00 dB |
| 25 % | 0,54 dB | 3,98 dB |
| 50 % | 1,86 dB | 8,13 dB |
| 75 % | 4,28 dB | 12,15 dB |
| 100 % | 7,57 dB | 15,81 dB |

Le gain effectif diminue lorsque le niveau numérique augmente : à 100 % de Détails et 6 kHz, il passe d’environ +25,48 dB pour une source à -60 dBFS à +22,50 dB pour une source à -36 dBFS. Ce sont ici les gains absolus de la chaîne ON, pas les incréments du tableau. Il faut représenter ce comportement dynamique dans une approximation, sans conclure que le compresseur se trouve forcément dans ce module plutôt que dans un étage commun après le renforcement.

## Largeur : mélange et phase dépendants de la fréquence

Largeur modifie les transferts directs/croisés, et pas uniquement le volume global. Près de 1 kHz, à 50 %, le canal opposé atteint environ -3,69 dB par rapport au direct avec une phase relative de 165,5° ; à 100 %, environ -1,93 dB et 165,0°. Près de 6 kHz, les phases et rapports sont différents. Une simple duplication, un délai unique ou un gain Side constant ne décrivent donc pas toute la réponse mesurée. Ces phases relatives sont calculées au sein d’une même acquisition et ne dépendent pas du retard global d’alignement.

Les bruits de contrôle confirment l’accentuation latérale. Source -48 dBFS ; variations de gain des bruits mono et en opposition de phase par rapport au réglage zéro, et corrélation sur le bruit indépendant :

| Largeur | Incrément bruit mono | Incrément bruit Side | Corrélation gauche/droite, bruit indépendant |
| ---: | ---: | ---: | ---: |
| 0 % | 0,00 dB | 0,00 dB | 0,051 |
| 25 % | 0,11 dB | 0,93 dB | -0,042 |
| 50 % | 0,23 dB | 1,28 dB | -0,068 |
| 75 % | 0,27 dB | 1,42 dB | -0,077 |
| 100 % | 0,27 dB | 2,28 dB | -0,175 |

Ce constat appuie un modèle stéréo à filtres dépendant de la fréquence. Il ne prouve ni une structure interne Mid/Side précise, ni que l’effet isolé est lui-même non linéaire : les traitements OEM communs peuvent interagir avec le nouveau mélange. Les données Mid/Side issues des balayages sont des estimations locales ; les bruits constituent un contrôle complémentaire.

## Volume Windows et répétabilité

| Effet seul à 50 % | Volumes comparés à 10 % | Écart maximal des gains de tonalités | P95 maximal des écarts spectraux directs |
| --- | --- | ---: | ---: |
| MaxxBass | 5 / 15 / 50 / 100 % | 2,00638 dB | 3,65011 dB |
| Détails | 5 / 15 / 50 / 100 % | 1,85067 dB | 2,93201 dB |
| Largeur | 5 / 15 / 50 / 100 % | 1,85414 dB | 2,96012 dB |

Les retours à zéro diffèrent de la première référence d’au plus 0,00449 dB sur les tonalités et 0,588 dB sur les transferts directs par balayage. Les écarts spectraux les plus importants se concentrent sur les premiers balayages à -60 dBFS : ils signalent une dépendance à l’historique/initialisation de la chaîne, sans en identifier la cause. Le fichier `zero-reference-envelope.csv` conserve min/médiane/max des références et les figures d’effets utilisent leur médiane.

Les comparaisons de volume doivent être appréciées par rapport à cette variabilité, pas par une hypothèse d’égalité parfaite. Elles concernent le signal numérique visible dans le loopback, sortie muette. Elles ne décrivent pas la variation acoustique, le comportement de l’amplificateur ou des protections à volume élevé.

## Contre-mesures ciblées du volume maximal

Les faibles volumes 5/10/15 % ne modifient pratiquement pas le signal capturé ici. À 100 %, en revanche, une correction fréquentielle supplémentaire de plusieurs dB apparaît pour les trois effets, au-delà de la variabilité des références. Cinq contre-mesures ont été ajoutées pour vérifier les trois boutons à zéro et répéter le passage 100 % → 10 % avec MaxxBass seul.

| Capture de contrôle | Comparée à | Écart maximal de gain des tonalités | P95 des écarts spectraux directs |
| --- | --- | ---: | ---: |
| zero-v100 | baseline-zero-first | 1,84735 dB | 2,92736 dB |
| zero-v50 | baseline-zero-first | 0,00449 dB | 0,58787 dB |
| zero-return-v10 | baseline-zero-first | 0,00449 dB | 0,58787 dB |
| bass-050-v100-repeat | bass-050-v100 | 0,00000 dB | 0,00000 dB |
| bass-050-v10-repeat | bass-050-v10 | 0,00320 dB | 0,00000 dB |

Ces contrôles permettent de distinguer la correction liée au volume d’un changement de position des effets. La courbe du contrôle tous boutons à zéro et celles des effets sont comparées dans `analysis/05-volume-controls.png`. Les retours à 10 % et répétitions à 100 % doivent être lus avec les tolérances de référence ci-dessus. Ce traitement est visible dans la chaîne commune ; son emplacement exact, logiciel ou matériel avant le loopback, n’est pas identifié. Il faut donc prévoir cette dépendance au volume dans la reconstruction globale, plutôt que l’attribuer automatiquement à chacun des trois boutons.

## Conséquences pour une reconstruction sous Linux

- Reproduire aussi la référence **Playback ON, trois boutons à zéro** : elle reste différente de Playback OFF. Les boutons à zéro ne rendent pas toute la chaîne neutre.
- Prévoir pour le grave un comportement dépendant du niveau, des harmoniques et une composante commune aux deux canaux ; un gros boost EQ fixe ne suffit pas.
- Modéliser la courbe et la dynamique observées avec Détails, tout en gardant ouverte l’hypothèse d’un étage dynamique partagé.
- Utiliser une véritable chaîne stéréo avec transferts entre canaux pour Largeur. Deux convolutions indépendantes L/R ne suffisent pas.
- Valider les modèles sur les mêmes fichiers source et sur le mélange d’origine capturé, avant de les appliquer aux haut-parleurs sous Linux. L’ordre des traitements et leurs interactions ne sont pas identifiés par les seuls essais un par un.

**Limites :** seuls trois niveaux numériques faibles sont caractérisés, jusqu’à -36 dBFS crête. Les seuils à niveau musical élevé, les constantes exactes d’attaque/relâchement, les effets d’ordre supérieur et les interactions entre modules ne sont pas identifiés. Il ne faut pas extrapoler une réponse ou un ratio de compression à tout signal. Les phases de transferts presque nuls sont inexploitées ; les planchers numériques dans les CSV ne sont pas des mesures de bruit acoustique. Aucune courbe acoustique des quatre haut-parleurs n’est fournie.

## Résultats disponibles et état final

- `analysis/01-spectral-isolation.png` : effet spectral de chaque bouton aux trois niveaux ; PDF également fourni.
- `analysis/02-width-stereo.png` : transferts croisés et décomposition Mid/Side apparente.
- `analysis/03-levels-harmonics.png` : dépendance au niveau et harmoniques.
- `analysis/04-endpoint-volume.png` : effet du volume Windows.
- `analysis/RESUME-NUMERIQUE.md` et `model-diagnostics.json` : chiffres détaillés.
- CSV complets : `transfers.csv`, `transfers-relative-to-zero.csv`, `tones.csv`, `tone-comparisons.csv`, `noise-stereo.csv`, `mid-side-apparent.csv`, `zero-reference-envelope.csv`.
- `manifest.json` : 36 acquisitions, empreintes vérifiées, états UI avant/après identiques, données finies, aucun écrêtage d’échantillons ni incident de callback PortAudio signalé. Cela ne constitue pas une preuve exhaustive d’absence d’anomalies.

Réglages d’origine restaurés et vérifiés : **MaxxBass 50 %, Détails 35 %, Largeur 35 %, Playback ON, Minuit OFF**, EQ inchangé, endpoint inchangé, volume et mute initiaux rétablis. Voir `restoration.json` et `states/restored-final-confirmed.png`. Aucun profil Linux ni pilote Windows n’a été remplacé. Les scripts et les données restent locaux.
