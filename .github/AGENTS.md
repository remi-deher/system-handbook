# Instructions pour les IA — Intégration GitHub

Lire `../AGENTS.md`, puis `README.md` ici.

Ce dossier est l'exception technique à la règle « seul dossier de contenu OS à la racine ». Il héberge la CI GitHub Actions ; il n'est pas une portée système et ne reproduit pas les neuf rubriques.

Conserver les guides standard `AGENTS.md` et `README.md` ici et dans ses sous-dossiers. Les guides numérotés restent obligatoires sous `OS/`.

`main` est protégé : aucun push direct, pull request obligatoire, fusion automatique en squash quand les deux contrôles sont verts, branche supprimée ensuite. Ne pas désactiver ces réglages (protection, fusion automatique, suppression des branches) pour faire passer un changement.

Ne pas affaiblir les contrôles obligatoires, ajouter d'exclusion globale de secrets, afficher de données sensibles, déchiffrer des objets ou fournir l'identité privée à la CI. Épingler les actions par SHA et les outils par version et checksum. Mettre à jour la documentation et vérifier les workflows après toute modification.
