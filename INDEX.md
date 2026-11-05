# Index du dépôt

Index généré automatiquement à partir des fiches : ne pas modifier à la main. Chaque ligne reprend le titre, le résumé et les métadonnées de la fiche. Version lisible par machine : [INDEX.json](INDEX.json). Navigation par dossiers : [README.md](README.md).

## Portées

- **[Portable Dell sous Arch](OS/Linux/arch/02-SYSTEME/MACHINES/portable-dell/README.md)** — Particularités de cette machine ; inventaire matériel à compléter uniquement à partir d’observations vérifiées.
- **[Claude Code sous Arch](OS/Linux/arch/04-LOGICIEL/claude-code/README.md)** — Documentation Claude Code dans la portée Arch ; préciser les versions réellement testées.
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

- **[Lecteur d'empreinte Broadcom 0a5c:5843 (Dell Latitude 7440)](OS/Linux/arch/02-SYSTEME/MACHINES/portable-dell/02-SYSTEME/lecteur-empreinte-broadcom.md)** — le lecteur d'empreinte Broadcom `0a5c:5843` du Dell Latitude 7440 demande `libfprint-tod` et le pilote propriétaire `libfprint-2-tod1-broadcom` (AUR) ; l'enregistrement se fait ensuite dans les paramètres Ryoku (Super + ,), rubrique « Écran de verrouillage ». (statut : testé (installation et configuration réalisées par l'utilisateur ; enregistrement vu en cours dans les paramètres Ryoku) ; date : 2026-11-05)
- **[EasyEffects : modèle « Waves ON » des haut-parleurs du Dell Latitude 7440](OS/Linux/arch/02-SYSTEME/MACHINES/portable-dell/03-CONFIGURATION/easyeffects-modele-waves-on.md)** — deux presets de sortie EasyEffects qui approchent le traitement audio Windows (Waves ON) des haut-parleurs intégrés, ajustés sur des mesures musicales ; à importer dans EasyEffects, en commençant par la variante -6 dB. (statut : proposé (modèle expérimental, rendu sonore non validé par écoute A/B) ; date : 2026-11-05)
- **[Claude Code en service systemd avec Remote Control](OS/Linux/arch/04-LOGICIEL/claude-code/02-SYSTEME/service-systemd-remote-control.md)** — un service systemd utilisateur lance `claude remote-control` au démarrage, ce qui garde une session Claude Code accessible depuis le téléphone ou claude.ai/code et la reprend après un redémarrage du service. (statut : testé (confirmé par l'utilisateur : session visible et synchronisée des deux côtés, reprise après redémarrage du service) ; date : 2026-11-05)
- **[setup-claude-remote-control : installer le service Remote Control](OS/Linux/arch/04-LOGICIEL/claude-code/05-SCRIPT/setup-claude-remote-control.md)** — script bash idempotent qui crée et active le service systemd utilisateur `claude-remote-control` ; sans chemin ni nom de machine en dur. (statut : testé (exécuté plusieurs fois, relance sans effet de bord) ; date : 2026-11-05)
- **[Remote Control : session introuvable, sans réponse ou service bloqué](OS/Linux/arch/04-LOGICIEL/claude-code/07-RESOLUTION/remote-control-session-introuvable.md)** — liste des pièges rencontrés avec `claude remote-control` en service (session absente de l'application, message sans réponse, erreur « already served », service actif mais mort) et leur cause. (statut : résolu (confirmé par l'utilisateur) ; certaines causes restent des hypothèses signalées comme telles ; date : 2026-11-05)
- **[polkit : « open /etc/pam.d/polkit-1: no such file or directory »](OS/Linux/arch/07-RESOLUTION/AUTHENTIFICATION/polkit-pam-introuvable.md)** — depuis PAM 1.7, Arch livre le fichier PAM de polkit dans `/usr/lib/pam.d/` et non dans `/etc/pam.d/` ; un outil qui lit `/etc/pam.d/polkit-1` échoue, et copier le fichier dans `/etc/pam.d/` règle le problème. (statut : résolu (confirmé par l'utilisateur) ; date : 2026-11-05)
- **[Créer et publier un plugin Ryoku](OS/Linux/arch/ryoku/05-SCRIPT/PLUGINS/creer-et-publier-un-plugin-ryoku.md)** — comment créer, valider, installer et publier un plugin de shell Ryoku, avec le dépôt généraliste `linux-plugins` et un miroir mono-plugin pour l'installation par URL. (statut : testé ; date : 2026-11-05)
- **[Écran de connexion Ryoku en QWERTY au lieu d'AZERTY](OS/Linux/arch/ryoku/07-RESOLUTION/AUTHENTIFICATION/greeter-clavier-qwerty.md)** — l'écran de connexion (greeter weston de SDDM) tape en QWERTY alors que le système est en `fr` ; ajouter `keymap_layout` à la section `[keyboard]` générée par `ryoku-greeter` règle le problème. (statut : résolu (confirmé par l'utilisateur, défaut reproduit avec l'ancien fichier) ; la cause exacte dans weston reste une hypothèse ; date : 2026-11-05)
- **[Lanceur Super+Espace sans résultat (variante hero)](OS/Linux/arch/ryoku/07-RESOLUTION/LANCEUR/lanceur-hero-sans-resultat.md)** — Sous Ryoku (Niri et Hyprland), le lanceur Super+Espace n'affiche aucun résultat avec la variante `hero` ; contournement en passant à la variante `main`, sans cause identifiée. (statut : contournement confirmé par l'utilisateur le 5 novembre 2026 ; cause non identifiée ; date : 2026-11-05)
- **[Raccourcis AZERTY dans Ryoku / Niri](OS/Linux/arch/ryoku/niri/07-RESOLUTION/CLAVIER/raccourcis-azerty.md)** — Les raccourcis Super+Alt et Super+Maj avec la rangée AZERTY déplacent une fenêtre vers un bureau ; ils exigent les noms XKB français et `focus=false` pour Maj dans Ryoku avec Niri. (statut : résolu et confirmé par l'utilisateur le 4 novembre 2026)

## Outils communs

- **[Chiffrer et récupérer — Linux / Bash](OUTILS/CHIFFREMENT/linux.md)** — Commandes Bash pour chiffrer un fichier ou un dossier avec age et tar vers un objet à nom opaque, puis le déchiffrer en retrouvant les noms d'origine.
- **[Chiffrer et récupérer — Windows / PowerShell](OUTILS/CHIFFREMENT/windows.md)** — Commandes PowerShell 5.1 et 7 pour chiffrer et déchiffrer avec age.exe et tar.exe sous Windows natif, avec les limites observées (noms japonais, ordre des tar.exe).
- **[Nettoyer les branches locales validées](OUTILS/GIT/nettoyer-branches.md)** — script bash qui supprime les branches locales (et leurs worktrees) dont les commits sont déjà dans une pull request fusionnée ou dans la branche par défaut, en conservant tout ce qui n'est pas publié. (statut : testé (dépôt jetable avec worktree ; simulation sur ce dépôt). La suppression réelle n'a pas été lancée sur le dépôt de travail ; date : 2026-11-05)

## Documents généraux

- **[Instructions pour les IA — Notes et outils des systèmes](AGENTS.md)** — Ce dépôt est la mémoire technique de l’utilisateur pour Linux et Windows : notes, résolutions, scripts, configurations, logiciels, installation, maintenance et sauvegarde.
- **[Chiffrement des fichiers et dossiers](CHIFFREMENT.md)** — Le dépôt utilise age pour chiffrer et tar pour conserver ensemble le contenu, les noms d’origine et l’arborescence.
- **[Contribuer à System Handbook](CONTRIBUTING.md)** — Ce dépôt public conserve des connaissances, configurations et outils système.
- **[System Handbook](README.md)** — Documentation personnelle des systèmes, configurations, résolutions et outils.
