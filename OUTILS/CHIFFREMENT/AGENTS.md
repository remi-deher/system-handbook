# Instructions pour les IA — Commandes de chiffrement

Lire `../../AGENTS.md`, `../AGENTS.md`, `README.md` et `../../CHIFFREMENT.md`.

Ce dossier documente les commandes natives age et tar, communes au dépôt, avec des variantes Bash/Linux et PowerShell/Windows. Ne pas réintroduire une implémentation de chiffrement maison sans besoin explicite.

Préserver les noms opaques, les noms originaux à l’intérieur du tar chiffré, les temporaires privés hors dépôt et l’absence de remplacement automatique d’une configuration active. Sous les anciennes versions de PowerShell, éviter les pipelines binaires et vérifier explicitement les codes de sortie des exécutables natifs.

Utiliser uniquement une phrase secrète interactive, sans fichier d’identité ni destinataire à clé publique. Ne jamais inclure de phrase secrète ou de référence d’accès. Après une modification, vérifier les commandes avec des données jetables si l’environnement est disponible et documenter honnêtement les plateformes exécutées ; ne pas annoncer Windows testé depuis un simple essai WSL ou Linux.
