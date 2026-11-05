# Reprise sous Windows — captures loopback WASAPI Dell Latitude 7440

- Résumé : consigne donnée à l'IA sous Windows pour mettre en place et réaliser les captures loopback WASAPI ; sert de protocole de départ.
- Statut : proposé
- Date : 2026-11-05

Tu travailles sous Windows sur mon Dell Latitude 7440. Je veux caractériser le traitement audio Dell/Waves MaxxAudio pour préparer un profil EasyEffects sous Linux. Je t’autorise à examiner la configuration audio, préparer des outils/scripts locaux, générer des signaux et effectuer des captures numériques WASAPI loopback de signaux de test. Réponds en français et avance de façon autonome sur les opérations réversibles nécessaires.

## Contexte à lire

Lis `LISEZ-MOI.md`, `RAPPORT-LINUX.md` et `validation-linux.json` dans ce dossier. Les originaux doivent être préservés. Le candidat SST reconstruit sous Linux ne correspond pas au rendu Windows entendu : manque de virtualisation stéréo, de clarté, de basses et de puissance. La banque de biquads extraite du registre reste une interprétation non confirmée. Aucune mesure acoustique Windows n’a été faite : il ne faut pas présenter ces coefficients comme une calibration mesurée ou une preuve des traitements effectivement actifs.

## Objectif et limite essentielle

Mettre en place une acquisition WASAPI loopback du périphérique de rendu Realtek réellement utilisé par les haut-parleurs, puis déterminer expérimentalement quels traitements Waves apparaissent dans cette capture. Une capture numérique peut se situer avant certains traitements APO, matériels ou d’amplificateur. Elle ne représente pas automatiquement le signal acoustique final et ne permet pas de mesurer les haut-parleurs.

N’utilise pas un microphone virtuel ou un câble audio virtuel à la place de la sortie Realtek : il pourrait changer le routage et contourner Waves. Utilise le loopback de l’endpoint de rendu Realtek en mode partagé WASAPI. Aucun microphone physique, aucune capture de l’environnement ou enregistrement de voix privée n’est autorisé par ce prompt. Les captures doivent contenir uniquement les signaux de test générés pour cette tâche ; interromps les autres lectures avant chaque acquisition.

## Travail à réaliser

1. Identifier les versions de Windows, Realtek, Waves et des outils disponibles, l’endpoint de rendu exact et son identifiant, le format partagé, la fréquence, les canaux, le volume, les améliorations audio, le mode spatial et le profil Waves sélectionné. Vérifier que la sortie est bien celle des haut-parleurs intégrés. Conserver cet inventaire et sauvegarder les réglages à modifier. Consulter les sources officielles correspondant aux outils/API retenus pour leurs comportements susceptibles d’avoir changé.

2. Préparer une méthode reproductible de capture loopback WASAPI, de préférence par script avec les outils déjà présents. Installer seulement les dépendances nécessaires et documenter leur version et leur provenance. Une alternative avec Audacity est acceptable si elle permet réellement le loopback de la sortie Realtek. Vérifier l’API et le périphérique de capture choisis, plutôt que supposer qu’une entrée « Stereo Mix » ou virtuelle est équivalente. Éviter toute conversion en MP3/AAC. Conserver des WAV sans perte, idéalement float32, au format natif de l’endpoint.

3. Générer un ensemble bref de signaux stéréo connus avec des marges de crête documentées : synchronisation, silence, bruit à graine fixe ou multisine, excitation large bande adaptée à l’estimation de réponse, et séquences gauche seule/droite seule pour étudier les transferts entre canaux. Utiliser des fondus et éviter les impulsions fortes, les balayages graves puissants et tout écrêtage. Préparer également des segments à différents niveaux numériques, espacés de silences, pour observer gain, compression, attaque/relâchement et éventuelles harmoniques.

4. Commencer par des signaux faibles, par exemple un pic numérique de -30 dBFS, avec un volume physique bas et confortable. Ne monte pas automatiquement le volume vers un niveau élevé. Le loopback peut fonctionner à faible volume, mais un mute ou une modification du volume peut aussi modifier la capture ou le traitement : vérifier ce comportement avec un bref essai. Ne pas supposer que le volume physique est absent de la capture. Si une mesure exige un niveau acoustique nettement supérieur, préparer l’essai et demander mon accord avant de le lancer.

5. Effectuer d’abord une paire pilote avec EXACTEMENT le même fichier, lecteur, endpoint, format, volume et réglages, en ne changeant que l’état Waves. Conserver quelques secondes de marge avant et après le signal. Éviter un lecteur en mode exclusif, RAW ou avec DSP supplémentaire qui contournerait les effets. Noter comment Waves est activé/désactivé et vérifier son état effectif dans l’interface. La présence d’un service ne prouve pas le traitement. Si le changement de réglage exige de rouvrir le flux, le faire de manière identique pour chaque condition. Ne pas désinstaller les pilotes, supprimer des APO ni modifier les protections d’amplificateur pour obtenir un bypass.

6. Vérifier les captures pilotes : signal présent, bonne sortie, bonne durée, absence de dropouts et d’écrêtage, alignement temporel, fréquence et canaux. Comparer Waves ON et OFF après alignement. Préserver les niveaux absolus ; produire séparément une comparaison à gain égal pour distinguer changement de volume et changement de timbre. Répéter une condition identique pour estimer la variabilité avant d’attribuer une petite différence à Waves.

7. Si les captures sont identiques ou presque alors que Waves change audiblement le son, ne pas conclure que Waves ne traite rien. Documenter que le loopback peut précéder le traitement, vérifier les états et le routage, puis rechercher une voie de capture numérique officiellement documentée qui inclut les effets si elle existe. Si aucune voie n’est démontrable, terminer l’infrastructure et expliquer précisément pourquoi une mesure acoustique sera nécessaire. Ne pas fabriquer une réponse Waves à partir de captures sans différence démontrée.

8. Si une différence reproductible apparaît, compléter les acquisitions ON/OFF à plusieurs niveaux numériques prudents, avec les mêmes paramètres. Pour isoler les fonctions, essayer lorsque l’interface le permet : Waves désactivé, Waves activé avec son profil d’usage, puis activation séparée des fonctions spatiales, basses et clarté. Journaliser chaque état exact ; ne pas inventer de commandes ou de paramètres Waves non exposés. Restaurer les réglages d’origine à la fin.

9. Analyser les captures en distinguant réponse fréquentielle, gain, dynamique, distorsion et spatialisation. Exploiter les excitations gauche/droite pour estimer les quatre transferts L→L, L→R, R→L, R→R et leurs délais/phases lorsque le rapport signal/bruit le permet. Tester la dépendance au niveau et la répétabilité avant de proposer une réponse impulsionnelle : un seul convolver ne représente pas un traitement non linéaire ou variable dans le temps. Ne pas normaliser arbitrairement les captures ou impulsions.

10. Produire une synthèse exploitable pour Linux : observations réellement mesurées, traitements visibles dans le loopback, traitements possiblement absents, et pistes EasyEffects justifiées. Ne pas remplacer automatiquement le profil Linux existant avec une nouvelle approximation sans validation des acquisitions. Une référence Windows acoustique reste nécessaire pour établir la fidélité au son des haut-parleurs.

## Livrables dans ce dossier

Créer un sous-dossier `Mesures-Windows-WASAPI` avec :

- un inventaire de la machine et des réglages initiaux ;
- les scripts reproductibles de génération, lecture, capture et analyse, ainsi que leurs dépendances ;
- les signaux de référence originaux et les captures WAV brutes, séparés des fichiers alignés ou transformés ;
- un manifeste JSON/CSV indiquant pour chaque capture : horodatage, état Waves et fonctions, identifiant endpoint, volume, format, fichier source et son empreinte, niveaux, méthode de capture et éventuelles anomalies ;
- un rapport court `RAPPORT-WASAPI.md` avec résultats, contrôles, limites, réglages restaurés et instructions de reprise sous Linux ;
- les réponses, matrices de transfert ou paramètres dynamiques seulement lorsque les données les justifient, en conservant leur niveau de validation.

Les captures et exports restent locaux. N’envoie aucun fichier à un service externe. Ne termine pas à un simple plan : prépare l’outillage, réalise les captures prudentes autorisées et les vérifications possibles, puis indique seulement les interventions physiques indispensables. Aucune absence de réponse ne vaut accord pour un microphone physique ou un essai à fort volume.
