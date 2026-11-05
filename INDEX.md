# Index du dépôt

Index généré automatiquement à partir des fiches : ne pas modifier à la main. Chaque ligne reprend le titre, le résumé et les métadonnées de la fiche. Version lisible par machine : [INDEX.json](INDEX.json). Navigation par dossiers : [README.md](README.md).

## Portées

- **[Portable Dell sous Arch](OS/Linux/arch/02-SYSTEME/MACHINES/portable-dell/README.md)** — Particularités de cette machine ; inventaire matériel à compléter uniquement à partir d’observations vérifiées.
- **[Firefox sous Arch](OS/Linux/arch/04-LOGICIEL/firefox/README.md)** — Documentation Firefox dans la portée Arch ; préciser les versions réellement testées.
- **[Git sous Arch](OS/Linux/arch/04-LOGICIEL/git/README.md)** — Documentation Git dans la portée Arch.
- **[Kitty sous Arch](OS/Linux/arch/04-LOGICIEL/kitty/README.md)** — Documentation Kitty dans la portée Arch ; préciser les versions réellement testées.
- **[Arch](OS/Linux/arch/README.md)** — Famille Arch ; les contenus communs à Ryoku et Omarchy peuvent être rangés ici.
- **[Omarchy](OS/Linux/arch/omarchy/README.md)** — Environnement Omarchy dans la famille Arch ; squelette prêt à documenter.
- **[Ryoku](OS/Linux/arch/ryoku/README.md)** — Environnement Ryoku dans la famille Arch ; les adaptations de compositeur vont dans leur branche.
- **[Hyprland sous Ryoku](OS/Linux/arch/ryoku/hyprland/README.md)** — Compositeur Hyprland dans Ryoku ; squelette prêt à documenter.
- **[Niri sous Ryoku](OS/Linux/arch/ryoku/niri/README.md)** — Compositeur Niri dans Ryoku ; configuration et raccourcis spécifiques.
- **[Debian](OS/Linux/debian/README.md)** — Portée Debian ; aucune procédure spécifique n’est encore validée.
- **[Fedora](OS/Linux/fedora/README.md)** — Portée Fedora ; aucune procédure spécifique n’est encore validée.
- **[Ubuntu](OS/Linux/ubuntu/README.md)** — Portée Ubuntu ; aucune procédure spécifique n’est encore validée.
- **[Windows](OS/Windows/README.md)** — Portée Windows ; préciser édition, version et shell.

## Fiches

- **[Lanceur Super+Espace sans résultat (variante hero)](OS/Linux/arch/ryoku/07-RESOLUTION/LANCEUR/lanceur-hero-sans-resultat.md)** — Sous Ryoku (Niri et Hyprland), le lanceur Super+Espace n'affiche aucun résultat avec la variante `hero` ; contournement en passant à la variante `main`, sans cause identifiée. (statut : contournement confirmé par l'utilisateur le 5 novembre 2026 ; cause non identifiée ; date : 2026-11-05)
- **[Raccourcis AZERTY dans Ryoku / Niri](OS/Linux/arch/ryoku/niri/07-RESOLUTION/CLAVIER/raccourcis-azerty.md)** — Les raccourcis Super+Alt et Super+Maj avec la rangée AZERTY déplacent une fenêtre vers un bureau ; ils exigent les noms XKB français et `focus=false` pour Maj dans Ryoku avec Niri. (statut : résolu et confirmé par l'utilisateur le 4 novembre 2026)

## Outils communs

- **[Chiffrer et récupérer — Linux / Bash](OUTILS/CHIFFREMENT/linux.md)** — Commandes Bash pour chiffrer un fichier ou un dossier avec age et tar vers un objet à nom opaque, puis le déchiffrer en retrouvant les noms d'origine.
- **[Chiffrer et récupérer — Windows / PowerShell](OUTILS/CHIFFREMENT/windows.md)** — Commandes PowerShell 5.1 et 7 pour chiffrer et déchiffrer avec age.exe et tar.exe sous Windows natif, avec les limites observées (noms japonais, ordre des tar.exe).

## Documents généraux

- **[Instructions pour les IA — Notes et outils des systèmes](AGENTS.md)** — Ce dépôt est la mémoire technique de l’utilisateur pour Linux et Windows : notes, résolutions, scripts, configurations, logiciels, installation, maintenance et sauvegarde.
- **[Chiffrement des fichiers et dossiers](CHIFFREMENT.md)** — Le dépôt utilise age pour chiffrer et tar pour conserver ensemble le contenu, les noms d’origine et l’arborescence.
- **[Contribuer à System Handbook](CONTRIBUTING.md)** — Ce dépôt public conserve des connaissances, configurations et outils système.
- **[System Handbook](README.md)** — Documentation personnelle des systèmes, configurations, résolutions et outils.
