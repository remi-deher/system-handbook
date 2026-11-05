# Profil Windows actuel — protocole approfondi

- Résumé : protocole approfondi de mesure du profil Windows actuel (MaxxBass 50 %, Détails 35 %, Largeur 35 %) sur tous les volumes.
- Statut : testé (mesures réalisées sous Windows, profils non validés à l'écoute)
- Date : 2026-11-05

Objectif : fournir une référence électrique mieux caractérisée pour améliorer le profil EasyEffects sous Omarchy jugé trop faible, peu clair et insuffisamment stéréo. Cette session fonctionne sous Windows ; le nouveau profil Linux n'est pas disponible dans les fichiers inspectés. Aucune comparaison numérique directe avec lui ne doit donc être inventée.

## État figé

L'inventaire et la capture `states/initial-profile.*` font foi : Realtek, Waves Playback ON, MaxxBass 50 %, Détails 35 %, Largeur 35 %, Minuit OFF, dix bandes EQ à zéro. Le volume initial est 28 %. Les contrôles sont relus avant et après chaque acquisition. Les presets, les boutons et l'EQ restent inchangés ; seuls deux contrôles explicites Playback OFF sont prévus dans la série longue.

Le rendu matériel Realtek est enregistré par son analogue loopback WASAPI en mode partagé, float32 stéréo 48 kHz. Aucun microphone, câble virtuel ou mode RAW/exclusif. Le mode partagé et ses limites sont décrits dans la [documentation Microsoft](https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording).

La sortie physique reste muette pendant les essais, y compris à volume 100 % et pour les signaux numériques proches de la pleine échelle. Le mute est confirmé avant de relever le volume et surveillé pendant la lecture. Le volume initial est remis avant la levée du mute. La sonie électrique capturée ne représente donc ni des dB SPL ni la puissance acoustique à ce volume.

## Couverture prévue et couverture achevée

Le balayage dense envoie le même fichier de 5,65 s à **chaque volume entier 0..100 %**, avec répétitions initiales et parcours de retour. Il comporte conditionnement, balayages gauche/droite, bruit stéréo, mono, Side et tonalité. Le but est de repérer les transitions de correction/gain/stéréo selon le volume avec un stimulus invariant.

La suite longue approfondit plusieurs volumes représentatifs, dont le volume initial et maximal, ainsi que des points sélectionnés à partir du balayage dense. Elle comporte :

- les quatre transferts apparents entre canaux, par balayages gauche/droite à -48, -24 et -6 dBFS crête ;
- des tonalités 125/997/6000 Hz aux niveaux -60/-48/-36/-24/-18/-12/-6/-1 dBFS ;
- des changements de niveau sur porteuse continue 125/997 Hz, pour observer l'évolution temporelle du gain ;
- bruit rose indépendant à trois niveaux, bruits mono/Side/décorrélés ;
- deux tons 60 Hz/7 kHz (rapport 4:1) et 18/19 kHz pour sonder les produits d'intermodulation ;
- musique percussive synthétique originale, multisine dense, salves transitoires et signal à formants ;
- une phrase française synthétisée localement par SAPI vers un fichier, à deux niveaux, sans microphone ni lecture directe par SAPI.

Les fichiers source et leurs JSON donnent les durées, amplitudes, segments, graines et empreintes exactes. Aucun WAV source utilisé n'est normalisé ou modifié après acquisition. Les répétitions et contrôles permettent d'estimer variabilité et réversibilité.

Les listes `plan-*.json` décrivent le programme de travail ; **seul le manifeste final validé indique ce qui a réellement été achevé**. Tous les types de signaux longs ne sont pas rejoués à chaque point entier : le balayage dense et les essais approfondis constituent deux niveaux complémentaires de couverture.

## Méthodes indépendantes et catégories Windows

La lecture principale utilise PyAudioWPatch. Un lecteur partagé indépendant via `IAudioClient2` teste explicitement Other (0), Media (11), Movie (10), sans offload et sans RAW. Les catégories peuvent influencer les traitements du système ; elles sont documentées par [Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/audiosessiontypes/ne-audiosessiontypes-audio_stream_category) et configurées par [SetClientProperties](https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudioclient2-setclientproperties). Ce contrôle n'affirme pas qu'un navigateur ou lecteur employant un offload matériel suit le même chemin.

La sonie intégrée est calculée par pyloudnorm, filtre DeMan, méthode BS.1770-4. Le programme ne revendique pas une certification BS.1770-5. Les estimations de crête inter-échantillon utilisent une interpolation SciPy 4x ; elles sont comparées sur des fichiers sélectionnés au filtre ebur128/true-peak de FFmpeg. Les valeurs sources et sorties sont conservées séparément, sans correction de gain implicite. Sources : [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm), [FFmpeg ebur128](https://www.ffmpeg.org/ffmpeg-filters.html), [ITU BS.1770](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/en).

FFmpeg provient d'un fournisseur de binaires référencé par [ffmpeg.org](https://ffmpeg.org/download.html). Il reste local sous `tools/`. Version et empreinte figurent dans les résultats de contre-vérification. Les fichiers audio et exports ne sont envoyés à aucun service externe.

## Interprétation des mesures

Les transferts complexes sauvegardés en NPZ ont les axes `[niveau, sortie, entrée, fréquence]`. Ils représentent des réponses apparentes, dépendantes de l'excitation et du niveau, d'une chaîne potentiellement non linéaire. Ils ne constituent pas automatiquement une matrice de convolution universelle. La phase globale dépend de l'alignement sur le premier balayage ; les rapports croisé/direct d'une même capture sont plus adaptés aux comparaisons stéréo.

La fondamentale et les harmoniques sont estimées par ajustement simultané sinus/cosinus/DC. Les harmoniques retenues s'arrêtent à l'ordre 8 et 20 kHz : à 6 kHz seules les harmoniques 2 et 3 sont présentes dans la métrique. Les produits d'intermodulation exportés sont un sous-ensemble défini dans le script, pas une mesure normative certifiée SMPTE/CCIF.

Les enveloppes de gain utilisent une fenêtre de 40 ms et un pas de 20 ms. Elles permettent de comparer la récupération et la compression, mais ne donnent pas directement les constantes internes exactes du DSP : fenêtre et retard d'alignement résiduel limitent la précision temporelle.

La suite de récupération réserve 10 s à la référence faible et 15 s après chacune des trois excitations fortes. Un contrôle supplémentaire à 100 % emploie le lecteur natif indépendant et son tampon de 100 ms. Les fenêtres tardives (5–14,9 s) présentant un résidu d'ajustement harmonique supérieur à −20 dB sont signalées et exclues de l'interprétation en simple gain ; leur cause n'est pas attribuée au compresseur. Les dernières 100 ms sont exclues pour éviter le fondu final. Le résumé donne les centres et le nombre des fenêtres, qui se chevauchent et ne représentent donc pas autant d'événements distincts. Les WAV restent intacts.

Les matrices NPZ contiennent un masque de validité 80–16000 Hz. Les valeurs hors masque ne doivent pas être employées pour synthétiser un filtre. Le contrôle du script de comparaison utilise deux fois le même fichier Windows : il vérifie le logiciel, sans constituer une mesure du preset Linux.

Les rapports de bandes « présence » et grave/médium sont des indicateurs spectraux électriques. Ils ne sont pas des mesures acoustiques C50/C80, STI, intelligibilité ou jugement perceptif de clarté. La phrase TTS et les sons synthétiques ne remplacent pas toute la diversité des enregistrements musicaux réels.

Les signaux forts servent volontairement à caractériser la limitation : des échantillons au niveau pleine échelle ne doivent pas être supprimés ou normalisés. Un incident d'acquisition est distingué d'une saturation du traitement réellement observée.

## Reprise et traçabilité

Deux interruptions de l'accès UI ont été conservées sous `events/`. Les contrôles sont désormais recherchés à nouveau lorsque le cadre UWP est recréé ; si nécessaire, seule la page Lecture est réaffichée. Une capture dont le profil n'a pas pu être vérifié n'est pas validée. Les acquisitions déjà vérifiées ne sont pas écrasées lors d'une reprise.

Le volume et le mute initiaux sont restaurés dans un bloc `finally`. Aucun pilote, protection d'amplificateur, registre de réglage ou profil Linux n'est modifié. Une mesure acoustique et la vérification du fonctionnement physique des quatre haut-parleurs sous Linux restent nécessaires pour conclure sur la puissance réelle et la fidélité au son entendu.

Le dernier contrôle natif a terminé son acquisition, puis sa capture d'écran de restauration a rencontré un refus de premier plan Windows. La comparaison de handles a été corrigée en déclarant le type de retour HWND 64 bits. L'état audio a été relu séparément : volume 28 %, mute OFF et réglages initiaux conservés ; le manifeste final effectue une nouvelle vérification. L'erreur et les journaux sont conservés.
