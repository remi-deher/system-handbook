# EasyEffects : modèle « Waves ON » des haut-parleurs du Dell Latitude 7440

- Résumé : deux presets de sortie EasyEffects qui approchent le traitement audio Windows (Waves ON) des haut-parleurs intégrés, ajustés sur des mesures musicales ; à importer dans EasyEffects, en commençant par la variante -6 dB.
- Statut : proposé (modèle expérimental, rendu sonore non validé par écoute A/B).
- Date : 2026-11-05.
- Portée : Arch Linux, machine Dell Latitude 7440, EasyEffects ; sortie « Haut-parleurs » intégrée.
- Environnements testés : EasyEffects 8.3.2 présent sur la machine ; le chargement des presets et leur rendu ne sont pas confirmés ici.
- Prérequis et exclusions : EasyEffects avec les plugins LSP (stereo tools, égaliseur, compresseur multibande, limiteur). Ne concerne ni le casque, ni le Bluetooth, ni le HDMI.

## But ou problème

Retrouver sous Linux un rendu proche de celui de Windows avec Waves actif sur les haut-parleurs intégrés. Les presets reproduisent le **signal numérique envoyé vers l'ampli** (mesuré en loopback sous Windows sur 6 extraits musicaux et vocaux à 3 niveaux), pas la réponse acoustique des haut-parleurs.

## Fichiers

- [Dell Latitude 7440 - modèle Waves ON (mesures musique).json](Dell%20Latitude%207440%20-%20mod%C3%A8le%20Waves%20ON%20%28mesures%20musique%29.json) : même niveau numérique que Windows ON.
- [Dell Latitude 7440 - modèle Waves ON (mesures musique, -6 dB).json](Dell%20Latitude%207440%20-%20mod%C3%A8le%20Waves%20ON%20%28mesures%20musique%2C%20-6%20dB%29.json) : identique, avec -6 dB en sortie du limiteur (`output-gain`). **Point de départ conseillé.**

Les deux fichiers ne diffèrent que par cette valeur.

## Chaîne d'effets (sortie)

1. Stereo Tools `LR > MS`.
2. Égaliseur IIR 20 bandes, canaux séparés (gauche = Mid, droite = Side).
3. Stereo Tools `MS > LR`.
4. Compresseur multibande à 5 bandes (coupures 120, 500, 2000 et 6000 Hz).
5. Limiteur (seuil -0,3 dB, lookahead 5 ms).

D'après l'ajustement : graves ramenés en mono et fortement relevés, médiums élargis, compression forte (ratios de 2,8:1 à 8:1) et plafond de sonie vers -8 LUFS.

## Procédure ou utilisation

Shell : bash ou fish, sur Arch.

1. Copier les presets dans le dossier de sortie d'EasyEffects :

   ```bash
   mkdir -p ~/.local/share/easyeffects/output
   cp "Dell Latitude 7440 - modèle Waves ON (mesures musique).json" "Dell Latitude 7440 - modèle Waves ON (mesures musique, -6 dB).json" \
      ~/.local/share/easyeffects/output/
   ```

   Une autre voie consiste à importer le fichier depuis l'interface (effets de sortie, menu des presets).
2. Choisir la sortie « Haut-parleurs », puis charger un preset dans l'interface ou en ligne de commande. Le nom du preset est celui du fichier sans l'extension (à mettre entre guillemets, car il contient des espaces) :

   ```bash
   easyeffects --load-preset 'Dell Latitude 7440 - modèle Waves ON (mesures musique, -6 dB)'
   ```

3. Commencer à faible volume, avec la variante -6 dB. Comparer à volume perçu égal (A/B), sur de la musique puis de la voix.

## Validation

- Simulation Python du modèle sur 18 captures : erreur Mid par tiers d'octave de 2,1 dB RMS (9,8 dB sans traitement), erreur Side de 3,0 dB RMS sur les morceaux stéréo, sonie plus basse d'environ 1 dB que Windows.
- Les clés des presets viennent du code source d'EasyEffects ; leur chargement réel et le rendu sonore restent à vérifier.

## Limites

- Le niveau de la variante sans atténuation est celui de Windows ON, très fort (environ +14 à +23 LU par rapport à OFF).
- Le compresseur LSP n'est pas identique à la simulation (détection, lissage, coupures) ; les temps d'attaque et de relâchement (20 et 200 ms) n'ont pas été ajustés.
- Les valeurs de l'égaliseur viennent de 6 extraits, dont 3 réellement stéréo ; à revalider sur d'autres morceaux.
- Haut-parleurs, ampli et protections thermiques ou mécaniques n'ont pas été mesurés.
- Hypothèse : Linux envoie au codec le même signal numérique que Windows après Waves.

## Persistance et maintenance

Une mise à jour d'EasyEffects peut changer le format des presets ; si un plugin ne se charge pas, l'erreur d'import indique la clé fautive. Les données de mesure d'origine sont conservées hors dépôt.

## Sauvegarde et retour arrière

Les presets sont des ajouts : supprimer les deux fichiers de `~/.local/share/easyeffects/output/` suffit pour revenir en arrière. Sauvegarder `~/.config/easyeffects` avant tout changement d'autoload.
