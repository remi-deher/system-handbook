# Lecteur d'empreinte Broadcom 0a5c:5843 (Dell Latitude 7440)

- Résumé : le lecteur d'empreinte Broadcom `0a5c:5843` du Dell Latitude 7440 demande `libfprint-tod` et le pilote propriétaire `libfprint-2-tod1-broadcom` (AUR) ; l'enregistrement se fait ensuite dans les paramètres Ryoku (Super + ,), rubrique « Écran de verrouillage ».
- Statut : testé (installation et configuration réalisées par l'utilisateur ; enregistrement vu en cours dans les paramètres Ryoku).
- Date : 2026-11-05.
- Portée : Arch Linux, machine Dell Latitude 7440, environnement Ryoku.
- Environnements testés : Arch (noyau 7.2.x), fprintd 1.94.5, `libfprint-tod` 1.95.2+tod1, `libfprint-2-tod1-broadcom` 5.15.021.0, Ryoku Arch (paramètres).
- Prérequis et exclusions : accès AUR (`yay`), mot de passe sudo. Le paquet `libfprint-2-tod1-broadcom-cv3plus` vise les lecteurs `0a5c:586*` (ControlVault 3 Plus) et ne convient pas à `0a5c:5843`.

## But ou problème

Faire reconnaître le lecteur d'empreinte du portable. Avant l'installation, `fprintd` était présent mais inactif et `fprintd-list` répondait « No devices available ».

## Diagnostic

- Le lecteur apparaît dans la liste USB sous `0a5c:5843` (Broadcom BCM58200, nom USB « 58200 »).
- Aucun pilote libre de `libfprint` standard ne le gère : il faut le module TOD propriétaire de Dell/Broadcom, chargé par une `libfprint` compilée avec le support TOD.
- Le PKGBUILD AUR de `libfprint-2-tod1-broadcom` annonce explicitement la prise en charge de `0a5c:5843`.

## Procédure ou utilisation

Shell : fish ou bash, sur Arch.

1. Vérifier le lecteur :

   ```bash
   lsusb | grep -i 0a5c:5843
   ```

2. Installer la bibliothèque TOD (elle remplace `libfprint` et fournit `libfprint-2.so`, donc `fprintd` continue de fonctionner) et le pilote. `--ask 4` accepte le remplacement de `libfprint` :

   ```bash
   yay -S --ask 4 --needed libfprint-tod libfprint-2-tod1-broadcom
   ```

   La clé PGP du mainteneur de `libfprint-tod` (`D4C501DA48EB797A081750939449C2F50996635F`) est importée automatiquement par `yay` à la première compilation.

3. Enregistrer l'empreinte, au choix :
   - **Interface Ryoku** : ouvrir les paramètres (Super + ,), puis « Écran de verrouillage », section « Connexion, Empreinte & Clé de sécurité ». Choisir un doigt et suivre les étapes de capture (le lecteur demande plusieurs poses, « soulevez et retouchez »).
   - **Ligne de commande** : `fprintd-enroll`, puis `fprintd-verify`.

4. Dans la même section des paramètres, choisir où l'empreinte sert : déverrouillage de l'écran, `sudo`, écran de connexion, invites administrateur (polkit). Si l'option polkit échoue avec « open /etc/pam.d/polkit-1: no such file or directory », voir [la résolution dédiée](../../../../07-RESOLUTION/AUTHENTIFICATION/polkit-pam-introuvable.md).

## Validation

- Détection USB du lecteur et disponibilité des paquets AUR : constatées avant installation.
- Installation, configuration et enregistrement : réalisés par l'utilisateur ; une capture des paramètres Ryoku montre un enregistrement en cours (étape 10/11).
- Non vérifié ici : déverrouillage réel de l'écran, `sudo` et connexion par empreinte.

## Persistance et maintenance

- Une mise à jour de `libfprint` depuis les dépôts officiels est bloquée par le conflit avec `libfprint-tod` ; mettre à jour les deux paquets AUR ensemble.
- Le pilote installe aussi un micrologiciel dans `/var/lib/fprint/fw/` et des règles udev.

## Sauvegarde et retour arrière

Les empreintes sont stockées par `fprintd` sous `/var/lib/fprint/` et ne doivent jamais être versionnées. Pour revenir en arrière : `fprintd-delete "$USER"`, puis retirer `libfprint-2-tod1-broadcom` et `libfprint-tod` et réinstaller `libfprint`.

## Références

- [Dépôt Launchpad du pilote](https://git.launchpad.net/~oem-solutions-engineers/libfprint-2-tod1-broadcom/+git/libfprint-2-tod1-broadcom/)
- [Paquet AUR libfprint-2-tod1-broadcom](https://aur.archlinux.org/packages/libfprint-2-tod1-broadcom)
- [Paquet AUR libfprint-tod](https://aur.archlinux.org/packages/libfprint-tod)
