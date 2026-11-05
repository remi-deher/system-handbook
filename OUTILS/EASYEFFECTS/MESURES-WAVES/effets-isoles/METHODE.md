# Méthode — effets Waves isolés

- Résumé : méthode de la campagne qui isole MaxxBass, Détails et Largeur de Waves (loopback WASAPI, volumes, analyse, restauration).
- Statut : testé (mesures réalisées sous Windows, profils non validés à l'écoute)
- Date : 2026-11-05

Cette campagne complète `Mesures-Windows-WASAPI`. Les fichiers et résultats de la première campagne sont conservés.

## Référence et réglages

La première acquisition de cette campagne est `baseline-zero-first` : Waves Playback ON, MaxxBass 0 %, Détails 0 %, Largeur 0 %, Minuit OFF, dix bandes EQ à 0,0 dB. Les trois boutons ont été mis à zéro par l'utilisateur puis vérifiés par logiciel avant cette acquisition. Le contrôle global OFF est ensuite enregistré sous `master-off-zero`, toujours avec les trois boutons à zéro.

Les pourcentages et les états ON/OFF sont accessibles dans la propriété **UI Automation ItemStatus** des contrôles `cmdMaxxBass`, `cmdDetails`, `cmdWidth`, `cmdPower` et `cmdMidnight`. Cette découverte complète la limitation de la première campagne, qui n'avait pas relevé cette propriété. Les mouvements simulés par simple positionnement du curseur ne faisaient pas réagir les boutons ; des paquets de déplacement de souris injectés pendant le glisser fonctionnent. Le réglage s'effectue en boucle fermée jusqu'au pourcentage demandé, puis les valeurs de tous les effets et de l'EQ sont relues avant et après chaque acquisition. Une capture d'écran et un JSON accompagnent chaque état.

0 % est ici une **position de référence vérifiée** du bouton, pas une preuve que toute la chaîne Dell/Waves est neutre ou désactivée. Il faut analyser l'incrément d'un effet par rapport à cette référence, et garder le contrôle Playback OFF séparé.

Les positions isolées sont 25, 50, 75 et 100 % ; les deux autres boutons restent toujours à zéro. Après chaque bloc, une acquisition à zéro contrôle le retour à la référence. Une acquisition complémentaire reprend le mélange d'origine 50/35/35, sans servir de mesure isolée.

## Signaux et volumes

Le fichier unique `reference/isolation.wav` est stéréo float32, 48000 Hz, 34,3 secondes. Son empreinte et tous les segments figurent dans `reference/isolation.json`. Pour chacun des niveaux **-60, -48 et -36 dBFS crête**, il contient :

- un balayage logarithmique gauche seule et un droite seule, 65–18000 Hz, 1,5 s chacun ;
- des tonalités mono corrélées à 80, 125, 250, 997 et 6000 Hz, 0,6 s chacune ;
- du bruit à graine fixe, indépendant entre canaux, mono corrélé et en opposition de phase ;
- des silences et fondus courts. Un repère et des marges silencieuses encadrent l'ensemble.

Chaque condition reçoit exactement le même fichier. Les effets isolés sont d'abord mesurés à un volume Windows de 10 %. À 50 % d'effet, des essais complémentaires font varier le volume Windows : 5, 15, 50 et 100 %, soit cinq positions avec la référence 10 %. Ces positions sont le volume endpoint Windows, pas le niveau numérique du fichier : les deux variables sont distinctes.

**La sortie physique est muette pendant toutes les acquisitions.** Le loopback de ce périphérique conserve le signal traité en mode muet, comme vérifié lors de la première campagne. Pour les essais à 50/100 % de volume, le script impose et relit le mute avant de relever le volume. Il restaure le volume d'origine avant de rétablir l'état du mute. Aucune mesure acoustique à fort volume n'est effectuée, aucun microphone n'est ouvert. L'influence du volume mesurée ici concerne le DSP visible dans le loopback, pas la pression sonore, la distorsion ou les protections matérielles des haut-parleurs.

## Acquisition et analyse

La capture réutilise le loopback WASAPI de l'endpoint Realtek en mode partagé, sans périphérique virtuel ni RAW/exclusif. Le lecteur et l'endpoint sont identiques entre conditions. Chaque lecture ouvre de nouveaux flux. Le script refuse une autre session audio active non muette détectée avant lancement. Les valeurs brutes restent intactes : aucun auto-gain, aucune normalisation des WAV.

`analyze_campaign.py` aligne chaque acquisition sur le premier balayage gauche, vérifie les empreintes, les canaux, les valeurs finies, l'écrêtage et l'état UI, puis calcule :

- les quatre transferts apparents gauche/droite à chaque niveau, lissés en énergie sur 1/12 d'octave ;
- les incréments de magnitude par rapport à la référence tous effets à zéro ;
- une enveloppe min/médiane/max des références à zéro répétées, pour séparer la variabilité de référence des petits effets ; les figures spectrales utilisent cette médiane et le CSV conserve aussi l'écart à la toute première référence ;
- les rapports complexes canal opposé / canal direct, dont la phase relative ne dépend pas de l'alignement temporel global ;
- une décomposition Mid/Side apparente de la matrice des balayages séparés ;
- la fondamentale et les harmoniques, par ajustement simultané sinus/cosinus et DC, sur 100–200 ms puis 300–500 ms des tonalités ;
- les RMS Mid/Side, le gain et la corrélation des séquences de bruit.

Les harmoniques sont limitées à l'ordre 8 et à 20 kHz : à 6000 Hz seules les harmoniques 2 et 3 sont prises en compte. Les petites valeurs proches du plancher numérique ne sont pas des mesures acoustiques étalonnées de THD. Une variation de phase ou de délai ne doit pas être présentée comme une distorsion harmonique.

Une réponse calculée par balayage sur une chaîne non linéaire est une **réponse apparente dépendante de l'état, du niveau et de l'excitation**. La décomposition Mid/Side issue de balayages séparés suppose une stabilité suffisante pendant la mesure ; les bruits mono/side servent de vérification complémentaire. Ces données ne démontrent pas un noyau de convolution exact et universel. Trois niveaux et deux fenêtres temporelles ne suffisent pas à identifier un seuil, un knee et des constantes d'attaque/relâchement uniques.

Les données des deux premières campagnes restent nécessaires pour replacer ces effets dans la correction OEM globale. L'absence de variation dans le loopback lorsqu'on change le volume ne prouve pas une absence d'effets situés après ce point de capture.

## Exécution et restauration

Le runtime local reste `../Mesures-Windows-WASAPI/tools/python/python.exe`. Le dossier contient une copie locale `acquisition.py` de l'outil précédent, avec la garde supplémentaire pour les volumes élevés en mode muet. Les scripts `campaign.py`, `run_campaign.py` et `run_extra_volumes.py` ne doivent pas être lancés simultanément : ils contrôlent la même interface. Lancer un essai sous un nouveau label ; les WAV existants ne sont pas écrasés. Les reprises automatiques ne sautent que les acquisitions portant des métadonnées complètes et cohérentes.

`plan.json`, `plan-extra-volumes.json` et `plan-volume-controls.json` décrivent la campagne prévue ; **seul `manifest.json`, produit après vérifications finales, atteste la liste achevée**. Cinq contre-mesures complètent les 31 premiers essais : tous boutons à zéro aux volumes 100, 50 et 10 %, puis répétition MaxxBass seul à 50 % aux volumes 100 et 10 %. Les pilotes de campagne, y compris `run_volume_controls.py`, restaurent les trois positions initialement relevées, MaxxBass 50 %, Détails 35 %, Largeur 35 %, dans un bloc `finally`, et remettent Playback ON. `finalize_campaign.py` vérifie en plus l'endpoint, le volume et le mute initiaux ainsi que les 36 acquisitions attendues. Un arrêt forcé du processus ou une intervention manuelle peut empêcher cette restauration : toujours vérifier le fichier final et l'interface.

Source pour la propriété d'accessibilité : [Microsoft, AutomationElementInformation.ItemStatus](https://learn.microsoft.com/en-us/dotnet/api/system.windows.automation.automationelement.automationelementinformation.itemstatus?view=windowsdesktop-10.0). La valeur de pourcentage est fournie par l'application Waves ; son existence a été vérifiée sur cette installation.
