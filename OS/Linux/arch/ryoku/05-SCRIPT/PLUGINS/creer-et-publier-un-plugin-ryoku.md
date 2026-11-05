# Créer et publier un plugin Ryoku

Résumé : comment créer, valider, installer et publier un plugin de shell Ryoku, avec le dépôt généraliste `linux-plugins` et un miroir mono-plugin pour l'installation par URL.

- Statut : testé
- Date : 2026-11-05
- Portée : Ryoku (Arch), shell Quickshell ; Omarchy pour les mentions qui le concernent.
- Environnements testés : Ryoku 1.0.7, `ryoku plugin` et `ryostore` du paquet installé, bash et fish, GitHub avec `gh`. Publication Ryostore (`ryoku plugin share`) : **non testée**. Workflow `mirror.yml` : **non testé** (secret absent) ; le premier miroir a été poussé à la main.
- Prérequis : `ryoku`, `git`, `gh` connecté, un éditeur QML (`qmllint` aide).

## Ce que Ryoku accepte

| Mécanisme | Constat |
| --- | --- |
| `ryoku plugin add <url-git>` | clone le dépôt et exige `manifest.json` **à la racine** ; sur un dépôt multi-plugins : « aucun manifest.json » (testé) |
| `ryoku plugin add <dossier>` | accepte n'importe quel dossier local, donc un sous-dossier d'un clone (testé) |
| Catalogue Ryostore | dépôt central `ryoku-dev/ryostore`, un dossier `plugins/<id>/` par plugin, ajout par PR via `ryoku plugin share` (lu dans le cache, non testé) |
| Source de dépôt perso | aucun réglage trouvé dans le CLI, l'interface ni le cache ; je n'ai pas analysé le binaire en profondeur |
| Omarchy | `omarchy plugin add <url>` : même contrainte (`git clone`, `manifest.json` à la racine) |

Conséquence : un plugin = un dépôt pour l'installation par URL. Pour garder une collection, on utilise un dépôt généraliste comme source de vérité et un **miroir mono-plugin** alimenté par la CI.

## Organisation retenue

Dépôt [`remi-deher/linux-plugins`](https://github.com/remi-deher/linux-plugins) :

```text
linux/<environnement>/<plugin>/   un plugin autonome par dossier (manifest.json à sa racine)
mirrors.json                      dossier du plugin -> dépôt miroir
scripts/new-plugin.sh, validate-all.sh
.github/workflows/validate.yml, mirror.yml
CREDITS.md, AGENTS.md, LICENSE
```

## Procédure (bash ou fish)

1. Créer :

   ```bash
   cd ~/Projets/linux-plugins
   scripts/new-plugin.sh ryoku mon-plugin "Mon plugin"
   ```

   Équivaut à `ryoku plugin new <id> --bar --name N --to linux/ryoku` ; l'id est en minuscules, chiffres et tirets. Le dossier contient `AGENTS.md` : les règles R1–R11 que le validateur applique (dont R2 : tout fichier supplémentaire est listé dans `files`, R6 : commandes externes dans `dependencies.commands`, R8 : écriture seulement dans `stateDir`).
2. Écrire `service/Main.qml` (logique), `content/Widget.qml` (vue), `content/Panel.qml` (panneau de barre). Les noms de propriétés QML ne peuvent pas commencer par une majuscule : le panneau ne se charge pas sinon (le log est dans `/run/user/1000/quickshell/by-id/*/log.log`).
3. Valider : `ryoku plugin validate linux/ryoku/mon-plugin` (0 blocage requis) puis `scripts/validate-all.sh`.
4. Installer pour l'essayer :

   ```bash
   ryoku plugin add linux/ryoku/mon-plugin --bar --yes
   ryoku plugin remove mon-plugin     # nécessaire avant de réinstaller une nouvelle version
   ```

5. Crédits : si le plugin dérive d'un autre travail, garder le copyright de l'auteur dans `LICENSE`, ajouter une ligne à `CREDITS.md` et une section Credits au README du plugin.
6. Committer et pousser `linux-plugins`.
7. Installation par URL : créer le dépôt miroir et ajouter la ligne à `mirrors.json` :

   ```bash
   gh repo create remi-deher/mon-plugin --public
   git subtree split --prefix=linux/ryoku/mon-plugin -b mirror-tmp
   git push https://github.com/remi-deher/mon-plugin.git mirror-tmp:main && git branch -D mirror-tmp
   ```

   Puis `mirrors.json` : `"linux/ryoku/mon-plugin": "remi-deher/mon-plugin"`. Ensuite `mirror.yml` republie à chaque push sur `main` si le secret `MIRROR_TOKEN` existe (jeton à granularité fine, écriture sur le contenu des dépôts miroirs ; ne pas y mettre le jeton `gh` personnel).
8. Vérifier : `ryoku plugin add https://github.com/remi-deher/mon-plugin --bar --yes` (testé pour `ryoku-pods`).
9. Catalogue officiel (seulement sur décision) : `ryoku plugin share mon-plugin`.

## Validation

- Chaîne complète faite pour `ryoku-pods` : création du dépôt, miroir poussé à la main, installation par URL du miroir réussie.
- Non validé : `mirror.yml` en CI et `ryoku plugin share`.

## Retour arrière

`ryoku plugin remove <id>` ; un dépôt GitHub se supprime avec `gh repo delete` (confirmation requise). Le miroir est écrasé en force par la CI : ne jamais y committer à la main.

## Références

- [Fiche AirPods](../AIRPODS/README.md), exemple concret.
- Dépôts : [linux-plugins](https://github.com/remi-deher/linux-plugins), [ryoku-pods](https://github.com/remi-deher/ryoku-pods).
