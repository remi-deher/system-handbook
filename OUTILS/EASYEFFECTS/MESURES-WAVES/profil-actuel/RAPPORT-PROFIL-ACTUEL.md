# Référence Windows approfondie — Dell Latitude 7440

- Résumé : résultats de la référence Windows approfondie du profil actuel : gain, dynamique, stéréo et récupération.
- Statut : testé (mesures réalisées sous Windows, profils non validés à l'écoute)
- Date : 2026-11-05

**132 acquisitions validées**, dont les **101 volumes entiers de 0 à 100 %**, les répétitions, six contrôles avec un lecteur WASAPI indépendant, les suites longues et les contrôles de récupération. Cette campagne conserve le profil Windows actif : MaxxBass 50 %, Détails 35 %, Largeur 35 %, EQ plat, Minuit OFF. Le nouveau profil décevant est celui d’Omarchy ; il n’a pas été modifié ni comparé numériquement ici.

**Résultat principal : le rendu ne peut pas être décrit par une EQ, un gain fixe et un simple élargissement stéréo.** Les gains varient avec le niveau, le contenu, le volume Windows et l’historique du signal. Les fichiers fournissent des cibles électriques pour mesurer précisément ce qui manque sous Linux ; ils ne prouvent pas une correspondance acoustique des haut-parleurs.

Toutes les acquisitions sont effectuées en mode muet, sans microphone. Les volumes élevés et sources proches de la pleine échelle sont donc testés numériquement, sans faire jouer les haut-parleurs à ces niveaux. Le loopback observé précède l’atténuation physique : une sonie capturée à volume Windows 0 % ne représente pas un son audible à ce volume.

## 1. Couverture et différence avec les anciennes mesures

- Sonde de 5,65 s identique aux 101 positions du volume Windows : balayages L/R, bruit stéréo, mono et Side, tonalité. Répétitions initiales et parcours de retour.
- Suites de 93,02 s à plusieurs volumes représentatifs, de 0 à 100 %, avec le volume initial, répétitions et Playback OFF appariés.
- Tonalités à **-60, -48, -36, -24, -18, -12, -6 et -1 dBFS crête**, contre une limite de -36 dBFS dans la précédente campagne isolée.
- Matrices stéréo à trois niveaux, changements de niveau, intermodulation, bruit rose, musique percussive synthétique, multisine dense, salves et parole française TTS locale à deux niveaux.
- Récupération prolongée : même 997 Hz faible après 125 Hz, 6 kHz puis bruit fort, avec plateaux de 10 à 15 s.

Le balayage dense couvre chaque pourcentage ; tous les sons longs ne sont pas rejoués à chaque pourcentage. Les plans et le manifeste donnent la matrice exacte des essais. Les deux contrôles Playback OFF de la suite principale et celui de récupération désactivent cet interrupteur Waves, sans démontrer un bypass de tout le DSP Realtek.

## 2. Puissance et sonie selon le contenu

Gains de sonie intégrée par rapport au fichier source original, sans normalisation. Ces LU sont électriques : ils ne sont pas des dB SPL.

| Signal | Crête source | Gain LU, profil actif au volume initial | Gain LU, profil actif à 100 % | Gain LU, Playback OFF au volume initial |
| --- | ---: | ---: | ---: | ---: |
| Phrase TTS faible | -18 dBFS | 14,92 | 11,27 | -5,64 |
| Même phrase plus forte | -3 dBFS | 8,18 | 4,24 | -5,64 |
| Musique percussive synthétique | -3 dBFS | 4,73 | 1,53 | -7,48 |
| Multisine dense | -3 dBFS | 3,68 | 3,81 | -4,22 |
| Bruit rose stéréo | -3 dBFS | 3,40 | 3,40 | -4,29 |
| Transitoires courts | -1 dBFS | 3,81 | 4,87 | -3,39 |

La même phrase reçoit donc un gain différent selon son niveau ; la musique dense, les percussions et les transitoires reçoivent encore d’autres gains. Reprendre le gain trouvé sur une tonalité faible pour toute la musique peut provoquer une limitation excessive ou un niveau inadapté. Les indicateurs de crête, facteur de crête et bandes de présence sont également exportés ; ils ne constituent pas une note perceptive de clarté ou un test d’intelligibilité.

## 3. Courbes de niveau et limitation

Exemples au volume initial de 28 %, source mono corrélée. Gains de la fondamentale, canal L, fenêtre 350–600 ms. La séquence et son historique font partie de ces résultats : ce ne sont pas des paramètres universels de compresseur.

| Fréquence | Source | Fondamentale sortie | Gain effectif | Harmoniques retenues / fondamentale |
| ---: | ---: | ---: | ---: | ---: |
| 125 Hz | -48 dBFS | -21,64 dBFS | 26,36 dB | -54,66 dB |
| 125 Hz | -24 dBFS | -6,29 dBFS | 17,71 dB | -47,98 dB |
| 125 Hz | -6 dBFS | -0,65 dBFS | 5,35 dB | -42,13 dB |
| 125 Hz | -1 dBFS | -0,21 dBFS | 0,79 dB | -35,76 dB |
| 997 Hz | -48 dBFS | -51,35 dBFS | -3,35 dB | -85,25 dB |
| 997 Hz | -24 dBFS | -23,50 dBFS | 0,50 dB | -87,68 dB |
| 997 Hz | -6 dBFS | -9,88 dBFS | -3,88 dB | -66,53 dB |
| 997 Hz | -1 dBFS | -6,51 dBFS | -5,51 dB | -61,94 dB |
| 6000 Hz | -48 dBFS | -33,58 dBFS | 14,42 dB | -89,37 dB |
| 6000 Hz | -24 dBFS | -12,91 dBFS | 11,09 dB | -70,14 dB |
| 6000 Hz | -6 dBFS | -6,27 dBFS | -0,27 dB | -60,46 dB |
| 6000 Hz | -1 dBFS | -6,28 dBFS | -5,28 dB | -58,23 dB |

56 échantillons au total atteignent ou dépassent l’unité dans les captures concernées. Ils sont conservés et listés dans le manifeste : les signaux forts servent à caractériser la limitation, pas à être supprimés. Une saturation douce peut aussi exister sous 0 dBFS ; le seul comptage d’échantillons à l’unité ne suffit pas à décrire la distorsion.

## 4. Volume système et mélange stéréo

Sur la sonde et avec un critère exploratoire d’écart spectral P95 supérieur à 0,3 dB par rapport à 28 %, le premier point détecté est **51 %**. C’est un seuil d’observation pour ce stimulus et ce critère, pas le seuil interne exact d’un algorithme. Les spectres et la sonie évoluent ensuite ; la grille conserve les 101 valeurs.

Le volume initial 28 % vaut **-18,82 dB dans l’API Windows**. `windows-volume-law.csv` donne la correspondance complète. Les pourcentages Windows/Linux ne doivent pas être assimilés sans lire les gains réellement appliqués. La loi de volume, la correction DSP liée au volume et la réponse acoustique du matériel sont trois choses distinctes.

Les matrices complexes, rapports croisé/direct et phases montrent comment le mélange change selon fréquence, niveau et volume. Les fichiers NPZ ont les axes `[niveau, sortie, entrée, fréquence]` et un masque de validité 80–16000 Hz. **Ne pas convertir tous leurs bins bruts par IFFT en un filtre « exact »** : hors excitation, la division spectrale est fragile ; dans la bande, la chaîne demeure non linéaire et dépendante de l’historique. Les phases absolues dépendent de l’alignement, contrairement au rapport croisé/direct d’une même capture.

## 5. Mémoire et récupération entre bandes

La récupération est estimée sur un 997 Hz à -36 dBFS, après trois excitations fortes. La colonne temporelle est le premier retour dans ±0,5 dB du plateau tardif tenu pendant 0,5 s. Fenêtre de 40 ms, pas 20 ms : retard résiduel, fondus et fenêtrage sont inclus. Ce n’est pas une constante interne de release identifiée.

| Condition | Excitation précédente | Gain initial 40–140 ms | Gain tardif 13–15 s | Retour apparent dans ±0,5 dB |
| --- | --- | ---: | ---: | ---: |
| deep-recovery-native-v100 | tone_125_Hz | -1,30 dB | 3,23 dB | 1,62 s |
| deep-recovery-native-v100 | tone_6000_Hz | -5,15 dB | 3,23 dB | 4,12 s |
| deep-recovery-native-v100 | broadband_pink | 1,13 dB | 3,23 dB | 0,58 s |
| deep-recovery-off-v028 | tone_125_Hz | -3,02 dB | -3,02 dB | 0,04 s |
| deep-recovery-off-v028 | tone_6000_Hz | -3,02 dB | -3,02 dB | 0,04 s |
| deep-recovery-off-v028 | broadband_pink | -3,02 dB | -3,02 dB | 0,04 s |
| deep-recovery-v028 | tone_125_Hz | -4,90 dB | 1,40 dB | 2,36 s |
| deep-recovery-v028 | tone_6000_Hz | -7,34 dB | 1,40 dB | 4,22 s |
| deep-recovery-v028 | broadband_pink | -2,02 dB | 1,40 dB | 1,44 s |
| deep-recovery-v100 | tone_125_Hz | -1,30 dB | 3,23 dB | 1,62 s |
| deep-recovery-v100 | tone_6000_Hz | -5,15 dB | 3,23 dB | 4,12 s |
| deep-recovery-v100 | broadband_pink | 0,83 dB | 3,23 dB | 0,60 s |

Les traces complètes permettent de tester un modèle avec mémoire et de rechercher un couplage entre bandes. Un ratio calculé sur deux points d’une séquence ascendante ne suffit pas à identifier ce modèle.

## 6. Contre-vérifications et qualité

Des fenêtres tardives dont le résidu de la régression harmonique dépasse −20 dB sont signalées comme anomalies ; elles ne sont pas interprétées comme une commande de gain. Les 100 dernières millisecondes sont exclues pour éviter le fondu final. Le contrôle `deep-recovery-native-v100` utilise un lecteur indépendant et un tampon de 100 ms. Les WAV originaux sont conservés.

- `deep-recovery-v100`, après tone_6000_Hz : 6 fenêtres de 40 ms se chevauchant, centres [11.66, 11.68, 11.7, 12.72, 12.74, 12.76] s. Cause non identifiée ; voir les données brutes et `recovery-summary.json`.

- FFmpeg ebur128 et pyloudnorm/DeMan : écart maximal **0,043 LU** sur les fichiers contre-vérifiés. Estimation de crête 4x et FFmpeg : écart maximal **0,238 dB**. Versions, empreintes et journaux sont fournis.
- Lecteur indépendant IAudioClient2, catégories Other/Media/Movie : aucune différence notable selon les critères exploratoires choisis dans ce chemin partagé non offloadé. Voir `category-comparison.json` ; ce n’est pas une preuve pour tous les lecteurs ou chemins matériels.
- 132 WAV validés, empreintes et segments utiles vérifiés, états Waves relus, données finies, aucun incident de callback dans les acquisitions retenues. Les interruptions UI initiales sont tracées et les conditions manquantes ont été reprises.
- Les formes d’onde et les produits d’intermodulation sont mesurés électriquement ; pas de certification de mesure acoustique ou normative de THD/IMD.

## 7. Utilisation sous Omarchy

1. Vérifier le routage Linux et le fonctionnement des quatre transducteurs, sans déduire leur activation du simple nombre de canaux ALSA. Un défaut matériel/routage ne se corrige pas par une grosse EQ.
2. Envoyer **les fichiers source de `reference/`** dans le profil Linux actuel et enregistrer sa sortie numérique avant l’atténuation physique, en conservant les gains absolus et le format float. Vérifier d’abord ce point de capture avec un bypass et la source connue.
3. Comparer aux paires source/cible de `analysis/linux-evaluation-pairs.json` : LUFS, crêtes, dynamique, bandes et quatre transferts. Les cibles contiennent déjà le traitement Windows et ne doivent pas être retraitées par Waves/EasyEffects lors de cette comparaison.
4. Corriger séparément les écarts de niveau, réponse fréquentielle, dynamique et stéréo ; valider sur plusieurs contenus et niveaux. L’objectif n’est pas de rendre identique un seul balayage faible.
5. Si les résultats électriques deviennent proches alors que l’écoute reste très différente, contrôler le chemin matériel et prévoir une mesure acoustique avec accord et protocole adaptés.

## Fichiers et état final

- `manifest.json`, `restoration.json`, `inventory-initial.json` : couverture, contrôle et état du système.
- `reference/`, `captures/`, `states/`, `events/` : sources, captures brutes, preuves UI et interruptions.
- `analysis/files.csv`, `programmes.csv`, `tones.csv`, `matrices.csv`, `dynamics.csv`, `intermodulation.csv` : résultats détaillés.
- `analysis/compression-intervals.csv`, `recovery-summary.*`, `repeatability.json`, `windows-volume-law.csv`, `volume-grid.csv` : synthèses et contrôles.
- `analysis/cache/*-complex.npz` : matrices complexes apparentes avec axes, masque et référence de phase.
- Figures PNG/PDF `01-all-volumes` à `06-cross-band-recovery`. Scripts d’acquisition, génération et analyse joints.

Réglages initiaux restaurés : MaxxBass 50 %, Détails 35 %, Largeur 35 %, Playback ON, Minuit OFF, EQ inchangé, volume 28 %, mute initial rétabli. Aucun pilote, protection d’amplificateur ou profil Linux n’a été remplacé. Aucun microphone ouvert, aucun fichier audio envoyé à un service externe.

Les références physiques SPL et la comparaison au nouveau preset Omarchy restent à faire. Pour les méthodes, définitions et sources documentaires, consulter [METHODE.md](METHODE.md).
