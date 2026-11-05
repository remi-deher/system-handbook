# polkit : « open /etc/pam.d/polkit-1: no such file or directory »

- Résumé : depuis PAM 1.7, Arch livre le fichier PAM de polkit dans `/usr/lib/pam.d/` et non dans `/etc/pam.d/` ; un outil qui lit `/etc/pam.d/polkit-1` échoue, et copier le fichier dans `/etc/pam.d/` règle le problème.
- Statut : résolu (confirmé par l'utilisateur).
- Date : 2026-11-05.
- Portée : Arch Linux (famille), valable hors machine ou version précise.
- Environnements testés : Arch avec `polkit` 128-1 et `pam` 1.7.3-1, paramètres Ryoku ; pas d'autre environnement.
- Prérequis et exclusions : droits root. Ne concerne pas les systèmes dont le paquet polkit place encore son fichier dans `/etc/pam.d/`.

## But ou problème

Activer l'empreinte pour les invites administrateur (polkit) depuis les paramètres de Ryoku échoue avec :

```text
Impossible de mettre à jour invites admin: <hôte>: read /etc/pam.d/polkit-1: open /etc/pam.d/polkit-1: no such file or directory
```

Le même message peut apparaître avec tout outil qui édite `/etc/pam.d/polkit-1` (ajout de `pam_fprintd`, par exemple).

## Diagnostic

- `/etc/pam.d/polkit-1` n'existe pas. Le fichier appartient au paquet `polkit` et se trouve dans `/usr/lib/pam.d/polkit-1` (`pacman -Qo /usr/lib/pam.d/polkit-1`).
- PAM 1.7 lit aussi `/usr/lib/pam.d/` quand `/etc/pam.d/` n'a pas le service, donc l'authentification polkit fonctionne normalement ; seuls les outils qui lisent `/etc/pam.d/polkit-1` en dur échouent.
- Contenu d'origine du fichier :

  ```text
  #%PAM-1.0

  auth       include      system-auth
  account    include      system-auth
  password   include      system-auth
  session    include      system-auth
  ```

## Procédure ou utilisation

Shell : bash ou fish, sur Arch.

1. Copier le fichier du paquet dans `/etc/pam.d/`, sans le modifier :

   ```bash
   sudo install -m 644 /usr/lib/pam.d/polkit-1 /etc/pam.d/polkit-1
   ```

2. Relancer l'opération (par exemple réactiver « Invitations admin » dans les paramètres Ryoku). L'outil peut alors modifier le fichier et créer sa sauvegarde.

## Validation

Confirmé par l'utilisateur : après la copie, l'activation de l'empreinte pour les invites polkit fonctionne dans les paramètres Ryoku. Le test réel d'une invite polkit n'est pas détaillé ici.

## Persistance et maintenance

- La copie dans `/etc/pam.d/` prime sur celle de `/usr/lib/pam.d/` et n'est pas mise à jour par pacman. Si une mise à jour de `polkit` change son fichier PAM, comparer les deux avec `diff /usr/lib/pam.d/polkit-1 /etc/pam.d/polkit-1`.
- Le même mécanisme peut toucher d'autres services dont le fichier PAM est livré dans `/usr/lib/pam.d/` (`systemd-run0`, `systemd-user`).

## Sauvegarde et retour arrière

Pour revenir à l'état d'origine, supprimer la copie : `sudo rm /etc/pam.d/polkit-1`. Si un outil a créé une sauvegarde `polkit-1.*-bak`, la conserver tant que la modification est active.

## Références

- [Lecteur d'empreinte Broadcom 0a5c:5843](../../02-SYSTEME/MACHINES/portable-dell/02-SYSTEME/lecteur-empreinte-broadcom.md) : contexte (empreinte sur le Dell Latitude 7440).
