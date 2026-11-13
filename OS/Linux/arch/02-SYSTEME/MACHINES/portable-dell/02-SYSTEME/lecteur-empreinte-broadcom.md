# Lecteur d'empreinte Broadcom 0a5c:5843 (Dell Latitude 7440)

- Résumé : le lecteur d'empreinte Broadcom `0a5c:5843` du Dell Latitude 7440 demande `libfprint-tod` et le pilote propriétaire `libfprint-2-tod1-broadcom` (AUR) ; l'enregistrement se fait ensuite dans les paramètres Ryoku (Super + ,), rubrique « Écran de verrouillage ».
- Statut : installation, enregistrement d'une empreinte et fonctionnement confirmés par l'utilisateur le 2026-11-13 (réinstallation des paquets). Le 2026-11-08, le journal fprintd avait confirmé une désactivation pour surchauffe après des vérifications sans correspondance ; le verrouillage a alors été configuré pour garder une conversation PAM unique (`max-tries=-1`), mais son effet sur la surchauffe reste à confirmer après une période de verrouillage comparable.
- Date : 2026-11-13.
- Dernière vérification : 2026-11-13, sous Arch Linux (noyau 7.3.4-arch1-1), Ryoku 1.0.9, niri 26.04, fprintd 1.94.5-2, `libfprint-tod` 1.95.2+tod1-1, `libfprint-2-tod1-broadcom` 5.15.021.0-1.
- Portée : Arch Linux, machine Dell Latitude 7440, environnement Ryoku.
- Environnements : installation initiale sous Arch (noyau 7.2.x), fprintd 1.94.5, `libfprint-tod` 1.95.2+tod1, `libfprint-2-tod1-broadcom` 5.15.021.0 ; constat antérieur sous CachyOS (noyau 7.3.3-1) avec les mêmes versions des paquets ; réinstallation du 2026-11-13 sous Arch Linux (voir « Dernière vérification »).
- Prérequis et exclusions : accès AUR (`yay`), mot de passe sudo. Le paquet `libfprint-2-tod1-broadcom-cv3plus` vise les lecteurs `0a5c:586*` (ControlVault 3 Plus) et ne convient pas à `0a5c:5843`.

## But ou problème

Faire reconnaître le lecteur d'empreinte du portable. Avant l'installation, `fprintd` était présent mais inactif et `fprintd-list` répondait « No devices available ».

## Diagnostic

- Le lecteur apparaît dans la liste USB sous `0a5c:5843` (Broadcom BCM58200, nom USB « 58200 »).
- Aucun pilote libre de `libfprint` standard ne le gère : il faut le module TOD propriétaire de Dell/Broadcom, chargé par une `libfprint` compilée avec le support TOD.
- Le PKGBUILD AUR de `libfprint-2-tod1-broadcom` annonce explicitement la prise en charge de `0a5c:5843`.
- Lors d’un premier diagnostic après 10 à 20 minutes, le lecteur était en `power/control=auto` et `runtime_status=suspended`, avec `usbcore.autosuspend=2`. L’autosuspend a été envisagé avant le diagnostic thermique ci-dessous.
- Pendant le verrouillage de session, l’indication d’empreinte passe en erreur après 30 à 60 secondes et affiche des échecs répétés sans toucher le lecteur. Le journal fprintd indique `Device disabled to prevent overheating`, après un résultat de vérification arrivé tardivement. La désactivation thermique est donc confirmée ; le lien avec les vérifications sans correspondance est cohérent avec les observations, mais reste à valider après modification de PAM.

## Procédure ou utilisation

Shell : fish ou bash, sur Arch.

1. Vérifier le lecteur. `lsusb` vient du paquet `usbutils`, absent d'une installation Ryoku minimale ; sans lui, lire directement sysfs (bash) :

   ```bash
   lsusb | grep -i 0a5c:5843
   # sans usbutils :
   for d in /sys/bus/usb/devices/*/; do [ -r "$d/idVendor" ] && echo "$(cat "$d/idVendor"):$(cat "$d/idProduct")"; done | grep -i 0a5c:5843
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

## Verrouillage Ryoku et essais répétés

Le service PAM du verrouillage utilise deux conversations séparées : une pour le scan d’empreinte et une pour le mot de passe. La valeur `timeout=-1` garde le scan actif sans limite de temps, mais le nombre d’essais PAM vaut par défaut 3. Après trois lectures sans correspondance, la conversation se termine et Ryoku en démarre une nouvelle. Pour conserver une conversation unique pendant toute la durée du verrouillage, le paramètre `max-tries=-1` supprime cette limite ; le processus du verrouillage gère sa durée de vie.

Dans `/usr/share/ryoku/lockscreen/qylock/quickshell-lockscreen/assets/pam/ryoku-lock`, la ligne devient :

```pam
auth sufficient pam_fprintd.so timeout=-1 max-tries=-1
```

Après modification de la source, relancer `ryoku-qylock-activate` pour régénérer et activer les fichiers du verrouillage. La même ligne doit être présente dans `~/.local/share/quickshell-lockscreen/assets/pam/ryoku-lock`. Une mise à jour de `ryoku-desktop` peut écraser le fichier fourni sous `/usr/share`.

Une règle udev pour empêcher l’autosuspend a été essayée, puis retirée : le journal a révélé une désactivation pour surchauffe, et garder le lecteur éveillé risquait d’aggraver ce symptôme. Aucun réglage permanent d’autosuspend n’est conservé.

## Validation

- Détection USB du lecteur et disponibilité des paquets AUR : constatées avant installation.
- Installation, configuration et enregistrement : réalisés par l'utilisateur ; une capture des paramètres Ryoku montre un enregistrement en cours (étape 10/11).
- Le 2026-11-08, `max-tries=-1` a été appliqué au service PAM du verrouillage et propagé par `ryoku-qylock-activate`. Le fonctionnement après 10 à 20 minutes de verrouillage reste à confirmer.
- Le 2026-11-13, après réinstallation : l'utilisateur a installé les deux paquets avec la commande de l'étape 2 (le mot de passe sudo est demandé de façon interactive) et enregistré l'empreinte par les paramètres Ryoku (Super + ,, « Écran de verrouillage »). `fprintd-list` voit le lecteur « Broadcom Sensors » avec une empreinte enregistrée (index droit) ; le journal fprintd indique que le micrologiciel du capteur est à jour. L'utilisateur confirme que le fonctionnement est bon, sans préciser quels usages ont été essayés (déverrouillage, `sudo`, connexion).
- Le journal fprintd contient un refus `Authorization denied … 'EnrollStart' … Not Authorized: net.reactivated.fprint.device.enroll`, antérieur à l'enregistrement réussi ; cause non identifiée, sans conséquence constatée.
- Le 2026-11-13, la ligne `pam_fprintd.so` du service de verrouillage (source sous `/usr/share/ryoku/lockscreen/...` et copie sous `~/.local/share/quickshell-lockscreen/...`) vaut `timeout=-1` **sans** `max-tries=-1` : la modification du 2026-11-08 n'a pas survécu à la réinstallation. Le risque de désactivation thermique après trois lectures sans correspondance est donc de nouveau présent tant que le réglage n'est pas réappliqué.
- Non vérifié : le détail des usages (déverrouillage réel de l'écran, `sudo`, connexion par empreinte).

## Persistance et maintenance

- Une mise à jour de `libfprint` depuis les dépôts officiels est bloquée par le conflit avec `libfprint-tod` ; mettre à jour les deux paquets AUR ensemble.
- Le pilote installe aussi un micrologiciel dans `/var/lib/fprint/fw/` et des règles udev.
- Le réglage `max-tries=-1` du verrouillage ne persiste pas : il est perdu à une mise à jour de `ryoku-desktop` ou à une réinstallation (constaté le 2026-11-13). Après l'un ou l'autre, relire la ligne `pam_fprintd.so` et la réappliquer si besoin.

## Sauvegarde et retour arrière

Pour rétablir la limite par défaut de trois essais, retirer `max-tries=-1` de `/usr/share/ryoku/lockscreen/qylock/quickshell-lockscreen/assets/pam/ryoku-lock`, puis relancer `ryoku-qylock-activate`.

Les empreintes sont stockées par `fprintd` sous `/var/lib/fprint/` et ne doivent jamais être versionnées. Pour retirer le pilote : `fprintd-delete "$USER"`, puis retirer `libfprint-2-tod1-broadcom` et `libfprint-tod` et réinstaller `libfprint`.

## Références

- [Dépôt Launchpad du pilote](https://git.launchpad.net/~oem-solutions-engineers/libfprint-2-tod1-broadcom/+git/libfprint-2-tod1-broadcom/)
- [Paquet AUR libfprint-2-tod1-broadcom](https://aur.archlinux.org/packages/libfprint-2-tod1-broadcom)
- [Paquet AUR libfprint-tod](https://aur.archlinux.org/packages/libfprint-tod)
- [Manuel Arch de `pam_fprintd(8)`](https://man.archlinux.org/man/pam_fprintd.8.en)
