# Instructions pour les IA — Mesures Waves du Dell Latitude 7440

Lire `../../../AGENTS.md`, `../../AGENTS.md`, `../AGENTS.md` et `README.md`.

Ce dossier conserve la méthode, les scripts et les rapports des campagnes faites par des IA pour caractériser le traitement Waves MaxxAudio du Dell Latitude 7440 sous Windows. Les données brutes (WAV, captures d'écran, exports de registre, inventaires matériels, manifestes) sont volontairement absentes : elles sont lourdes, contiennent des identifiants locaux et se régénèrent avec les scripts.

- Ne pas ajouter de WAV, de `tools/` (Python ou ffmpeg embarqués), d'export `.reg`, d'inventaire de périphériques ni de manifeste. Si des données brutes doivent être conservées, elles relèvent de [la procédure de chiffrement](../../../CHIFFREMENT.md), hors de ce dépôt.
- Ne jamais écrire dans le dépôt l'identifiant réel du périphérique audio Windows (`GUID-DU-PERIPHERIQUE` le remplace) ni un chemin utilisateur.
- Les scripts sont publiés tels qu'ils ont été exécutés : ils supposent la disposition d'origine décrite dans le README. Ne pas les « corriger » sans les retester sous Windows.
- Distinguer mesure, simulation et écoute : le modèle n'a pas été validé par écoute A/B.
