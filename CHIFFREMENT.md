# Chiffrement des fichiers et dossiers

Le dépôt utilise **age** pour chiffrer et **tar** pour conserver ensemble le contenu, les noms d’origine et l’arborescence. Ce sont des outils existants : aucune implémentation de chiffrement maison n’est nécessaire.

## Comprendre les clés

- La **clé publique** permet de chiffrer pour un destinataire, mais pas de déchiffrer. Elle peut être publiée.
- La **clé privée**, appelée identité dans age, permet de déchiffrer. Elle reste hors du dépôt et n’est jamais fournie à la CI.
- [`.age-recipients`](.age-recipients) est le fichier de configuration public lu par `age -R`. Il contient les clés publiques des destinataires, une par ligne ; ce n’est pas une sauvegarde des secrets.
- Un fichier **`.age`** est l’objet chiffré. Dans nos procédures, son nom externe est aléatoire et les noms d’origine sont conservés dans le tar chiffré.

Une personne disposant du dépôt peut chiffrer un nouvel objet pour toi sans connaître ta clé privée. Elle ne peut pas pour autant ouvrir les objets existants. Le chiffrement pour une clé publique ne prouve pas qui a créé l’objet : ne récupérer que les archives attendues et de confiance.

Conserver un moyen de récupération indépendant de la machine. Retrouver la même identité autorisée permet de déchiffrer sur un autre poste ; une nouvelle clé ne remplace pas l’ancienne. Modifier le fichier public ne rechiffre pas l’historique Git.

Le fournisseur et les références de stockage de l’identité privée ne sont pas documentés dans le dépôt. Ne jamais copier une clé privée dans une conversation, un argument de commande ou un fichier versionné. Les exemples utilisent un fichier d’identité externe déjà obtenu par un moyen local autorisé.

## Procédures par système

| Système | Procédure |
| --- | --- |
| Linux / Bash | [Commandes natives Linux](OUTILS/CHIFFREMENT/linux.md) |
| Windows / PowerShell | [Commandes natives Windows](OUTILS/CHIFFREMENT/windows.md) |

Le format est commun : un objet créé sous Linux peut être ouvert sous Windows, et inversement, avec une identité autorisée. Les exemples utilisent un tar temporaire sous Windows pour éviter de faire transiter un flux binaire dans les anciennes versions de PowerShell.

## Emplacement et noms

Tout fichier ou dossier peut être chiffré dans la rubrique adaptée : `03-CONFIGURATION/`, une catégorie de `07-RESOLUTION/`, ou `08-SAUVEGARDE/`. Aucun coffre central n’est imposé.

Utiliser un nom `<32-caractères-hex-aléatoires>.age`. Un fichier individuel doit aussi être placé dans un tar avant chiffrement si son nom d’origine doit être retrouvé à l’ouverture : age seul chiffre des octets, pas le nom du fichier d’entrée.

Une fiche peut contenir un lien neutre « Pièce chiffrée ». Ne pas publier à côté une table de correspondance, un manifeste lisible ou une description confidentielle. Le dossier et le lien révèlent une association ; choisir un rangement moins révélateur si cette relation est elle-même sensible. Taille, nombre d’objets et dates des commits restent visibles.

## Sauvegardes

`08-SAUVEGARDE/` décrit une action de sauvegarde ou d’archivage, ses contrôles, sa rétention et sa restauration. **Toutes ses données sont chiffrées**, même non sensibles ; seuls les guides et procédures Markdown restent lisibles.

Le chiffrement d’une configuration ou d’une pièce jointe à une résolution ne la transforme pas en sauvegarde : sa documentation garde son emplacement fonctionnel. Les commandes capturent les fichiers tels quels ; arrêter ou exporter proprement une application si ses fichiers nécessitent une capture cohérente.

## Récupération et limites

Déchiffrer dans un nouveau dossier privé hors dépôt. Attendre la réussite de age avant toute extraction, puis récupérer les noms d’origine avec tar sans écraser une configuration active.

Les commandes documentées n’installent rien automatiquement dans l’application. Les ACL, propriétaires et attributs spécifiques à un OS ne constituent pas une configuration portable ; contrôler les permissions et adapter le contenu avant application sur une autre plateforme.

Les fichiers temporaires en clair doivent rester hors dépôt. Leur suppression normale ne garantit pas l’effacement physique, l’absence de swap ni le nettoyage après un arrêt brutal. Ne jamais renommer un `.pending-*` laissé par un échec comme s’il avait été vérifié.

Le chiffrement doit précéder le premier ajout à Git. Ajouter un objet chiffré ne supprime pas un ancien texte clair de l’historique. Vérifier une récupération avant de considérer une archive comme sauvegarde utilisable.

## Contrôles locaux et CI

La configuration [.pre-commit-config.yaml](.pre-commit-config.yaml) est commune aux hooks locaux et à GitHub Actions. Les hooks standards, Gitleaks et le contrôle propre au dépôt vérifient les fichiers suivis, la nomenclature et la politique des données ; la CI ajoute l’historique et les tests du validateur.

Aucun scanner ne garantit l’absence de toute information privée. La CI ne reçoit aucune identité, ne déchiffre pas les objets et ne publie pas de rapport contenant des valeurs privées. Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les commandes locales et les protections serveur.

## Validation

Les commandes natives Linux sont vérifiées avec des données et une identité jetables. Les commandes PowerShell sont rédigées pour Windows PowerShell 5.1 et PowerShell 7, avec age et tar installés ; elles ne sont pas annoncées comme exécutées sur ce poste Linux. La CI contrôle les conventions et les hooks sur Linux et Windows, sans tester de données personnelles.

Le destinataire public et l’identité existante sont conservés. Les archives documentaires locales des anciennes étapes restent hors du dépôt ; aucune archive personnelle n’est ajoutée automatiquement.

## Références

- [age : installation et commandes officielles](https://github.com/FiloSottile/age).
- [Microsoft : tar sous Windows](https://learn.microsoft.com/en-us/windows/tar).
- [Microsoft : pipelines PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipelines).
- [GitHub : retirer des données sensibles de l’historique](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
