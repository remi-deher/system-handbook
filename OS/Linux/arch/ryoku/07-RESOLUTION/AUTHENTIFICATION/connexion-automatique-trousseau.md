# Connexion automatique, verrouillage et trousseau

Résumé : avec SDDM en connexion automatique, le trousseau de connexion ne reçoit pas le mot de passe au démarrage ; cette fiche explique le mode sans demande et ses conséquences sur la confidentialité.

- Statut : testé pour la configuration décrite ; sécurité et comportement au démarrage à vérifier selon le système.
- Date : 2026-11-16.
- Dernière vérification : 2026-11-25 ; noyau 7.3.4-arch1-2, Ryoku 1:1.1.0.r6233.g0bf1174-1, Niri 26.04-1, SDDM 0.21.0-7, gnome-keyring 1:51.1-1.
- Portée : Arch Linux, Ryoku, SDDM, Niri et GNOME Keyring ; shell Bash.
- Environnement testé : session Ryoku/Niri avec connexion automatique et verrouillage au lancement. Le délai réel avant apparition du verrou n'a pas été mesuré.

## Problème et diagnostic

La connexion automatique n'envoie pas de mot de passe à PAM : un trousseau `login` protégé ne se déverrouille donc pas automatiquement au début de la session. Un verrouillage lancé ensuite par le compositeur n'établit pas à lui seul que le trousseau sera déverrouillé.

Dans **Ryoku Hub → Lockscreen**, examiner les options du trousseau ; en terminal, `ryoku keyring status` indique le mode, l'autologin et l'état du trousseau sans afficher ses secrets. Vérifier les versions et l'état effectif avant toute modification.

## Solution observée et limites

Une solution testée consiste à retirer le mot de passe du trousseau dans Seahorse, puis à sélectionner le mode `never-ask` via `ryoku keyring set never-ask`. Les éléments du trousseau sont alors **en clair sur le disque** : toute personne ayant accès aux fichiers peut les lire, sous réserve des protections du disque et du compte. Le verrouillage de session ne chiffre pas ces fichiers. Choisir ce compromis seulement en connaissance de cause ; un trousseau chiffré reste une autre option.

Lors d'un essai, `ryoku keyring set never-ask --convert` a indiqué que le trousseau n'était pas chargé malgré son état déverrouillé. La cause n'a pas été établie ; l'échec ne justifie ni une réinitialisation ni la suppression du trousseau. Le changement a été effectué dans Seahorse, sans `--reset`.

La connexion automatique SDDM et le lancement du verrou dans `user.kdl` sont deux réglages distincts. Le verrou peut apparaître après le début de la session ; le délai et la protection effective doivent être testés. Ne pas modifier les fichiers PAM livrés par Ryoku.

## Retour arrière

Pour revenir à un trousseau protégé, définir d'abord son mot de passe dans Seahorse, puis sélectionner `unlock-on-login` dans Ryoku. Un déverrouillage par connexion PAM suppose une authentification fournissant ce mot de passe : avec l'autologin, une demande distincte peut rester nécessaire. Vérifier à nouveau avec `ryoku keyring status` et tester après connexion.

Pour supprimer la connexion automatique, retirer uniquement la configuration SDDM ajoutée à cet effet ; retirer aussi le lancement personnel du verrou dans `~/.config/niri/user.kdl` si le verrou immédiat après une connexion normale n'est pas souhaité. Préserver les autres réglages et valider Niri. Ne pas utiliser `--reset` sans sauvegarde et décision explicite.
