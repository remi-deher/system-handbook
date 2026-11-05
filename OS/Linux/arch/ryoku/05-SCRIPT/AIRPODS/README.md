# AirPods — Ryoku

Résumé : plugin de barre Ryoku (`ryoku-pods`) qui affiche batteries, mode d'écoute et réglages des AirPods, porté depuis le plugin Omarchy `omarchy-pods`.

- Statut : testé
- Date : 2026-11-05
- Portée : Ryoku (Arch), barre du shell
- Environnements testés : Ryoku 1.0.7, AirPods Pro 3, fish/bash. Batterie du boîtier non confirmée (le boîtier n'émet que couvercle ouvert).
- Prérequis : démon `librepods` modifié (voir ci-dessous), paquets `cmake ninja qt6-connectivity qt6-tools qt6-declarative pkgconf libpulse`.

## Sources et crédits

| Élément | Source | Auteur | Licence |
| --- | --- | --- | --- |
| Plugin d'origine (panneau, `Model.js`, démon modifié) | [thisisgm/omarchy-pods](https://github.com/thisisgm/omarchy-pods), commit `fff7fec` | **GM** (`thisisgm`) | MIT |
| Protocole AirPods (AAP sur L2CAP, annonces BLE), base du démon | [kavishdevar/librepods](https://github.com/kavishdevar/librepods) | **Kavish Devar** | GPLv3 |
| Port Ryoku (`ryoku-pods`) | ce dossier | Remi | MIT, avec le copyright de GM conservé |

Tout le travail de rétro-ingénierie du protocole revient à Kavish Devar ; le panneau, le fichier d'état et les verbes de contrôle du démon sont l'œuvre de GM. Le port se limite à l'adaptation au format de plugin Ryoku.

## Contenu

Le code du plugin vit dans le dépôt de plugins `linux-plugins`, car l'arborescence d'un plugin Ryoku (`bin/`, `content/`, `service/`…) ne suit pas les conventions de dossiers de ce handbook :

- Dépôt : `https://github.com/remi-deher/linux-plugins`, dossier `linux/ryoku/ryoku-pods` (**pas encore publié** à la date de la fiche).
- Miroir mono-plugin prévu pour l'installation par URL : `https://github.com/remi-deher/ryoku-pods` (alimenté par la CI ; `ryoku plugin add <url>` exige `manifest.json` à la racine).
- Copie locale : `~/Projets/linux-plugins/linux/ryoku/ryoku-pods/` (licence MIT avec le copyright de GM conservé).

## Installation (bash ou fish)

Le démon n'est pas inclus (source externe, GPLv3) :

```bash
git clone https://github.com/thisisgm/omarchy-pods ~/src/omarchy-pods
git clone https://github.com/remi-deher/linux-plugins ~/Projets/linux-plugins
ryoku plugin add ~/Projets/linux-plugins/linux/ryoku/ryoku-pods --bar --yes
~/.local/share/ryoku/plugins/ryoku-pods/bin/ryopods-setup ~/src/omarchy-pods
```

`ryopods-setup` installe les paquets manquants via `pkexec pacman` (invite polkit), compile le démon dans `~/.local` et active `librepods.service`. Le plugin lit `~/.local/state/librepods/status.json` et appelle `librepods-ctl` pour les changements.

## Validation

- `ryoku plugin validate` : 0 blocage, 2 avertissements attendus (les scripts d'installation écrivent dans `~/.local`).
- Test de `Model.js` : `deno run --allow-read tests/model.test.js` passe.
- Essai réel : menu et batteries des écouteurs confirmés par l'utilisateur ; batterie du boîtier non détectée tant que les écouteurs sont en place.

## Différences avec la version Omarchy

Pas de navigation clavier ni d'IPC, pas de réglage `ctlPath`, panneau refait avec le kit `Ryoku.PluginKit`, interface traduite en français selon la locale. Détails dans le README du dépôt du plugin.

## Retour arrière

`ryoku plugin remove ryoku-pods`, puis `bin/ryopods-remove ~/src/omarchy-pods` pour retirer le démon et les secrets d'appairage locaux.

Voir les [instructions IA](00-AGENTS.md) et [l'index parent](../README.md).
