# Créer et publier un plugin Ryoku

Résumé : comment créer, valider, installer et publier un plugin de shell Ryoku avec le dépôt `linux-plugins`, dont la CI crée seule le dépôt miroir mono-plugin à la fusion d'une pull request.

- Statut : testé
- Date : 2026-11-08
- Portée : Ryoku (Arch), shell Quickshell ; Omarchy pour les mentions qui le concernent.
- Environnements testés : Ryoku 1.0.7, `ryoku plugin` et `ryostore` du paquet installé, bash et fish, GitHub avec `gh`. Chaîne complète (PR, CI, fusion, création du miroir, installation par URL) faite pour `proton-vpn` le 2026-11-08. Non testés : `scripts/new-plugin.sh` (le plugin `proton-vpn` a été créé avec `ryoku plugin new` puis copié) et la publication Ryostore (`ryoku plugin share`).
- Prérequis : `ryoku`, `git`, `gh` connecté, `jq`, un éditeur QML (`qmllint` aide). Le dépôt `linux-plugins` cloné, par exemple dans `~/GitHub/linux-plugins`.

## Ce que Ryoku accepte

| Mécanisme | Constat |
| --- | --- |
| `ryoku plugin add <url-git>` | clone le dépôt et exige `manifest.json` **à la racine** ; sur un dépôt multi-plugins : « aucun manifest.json » (testé) |
| `ryoku plugin add <dossier>` | accepte n'importe quel dossier local, donc un sous-dossier d'un clone (testé) |
| Catalogue Ryostore | dépôt central `ryoku-dev/ryostore`, ajout par PR via `ryoku plugin share` (lu dans le cache, non testé) |
| Omarchy | `omarchy plugin add <url>` : même contrainte (`git clone`, `manifest.json` à la racine) |

Conséquence : un plugin = un dépôt pour l'installation par URL. `linux-plugins` est la source de vérité et sa CI publie chaque plugin dans un **miroir** en lecture seule.

## Organisation et règles du dépôt

Dépôt [`remi-deher/linux-plugins`](https://github.com/remi-deher/linux-plugins). Sa référence est son `AGENTS.md` ; en résumé :

```text
linux/<environnement>/<id>/   un plugin par dossier (manifest.json, README.md, LICENSE à sa racine)
scripts/new-plugin.sh, validate-all.sh, gen-index.sh, mirror.sh
.github/workflows/validate.yml, version.yml, mirror.yml
CREDITS.md, README.md (table générée), plugins.json (généré)
```

- L'`id` du manifest est égal au nom du dossier (le miroir porte ce nom).
- `main` n'accepte que des pull requests ; les miroirs sont en lecture seule. Ne jamais y pousser à la main.
- Il n'y a **ni `mirrors.json` ni Release GitHub** : ne jamais créer un dépôt miroir à la main.
- Messages de commit sans trailer co-auteur (règle de ce dépôt).
- Cycle de vie (`status` du manifest, `draft` si absent) : `draft` n'est jamais publié ; `experimental` et `stable` sont mis en miroir ; `deprecated` l'est avec un préfixe `[DEPRECATED]` ; `archived` est mis en miroir une dernière fois puis le miroir est archivé. Ne jamais supprimer un dossier de plugin.

## Procédure (bash ou fish)

1. Créer le plugin, en `draft` :

   ```bash
   cd ~/GitHub/linux-plugins
   git switch -c feat/mon-plugin
   scripts/new-plugin.sh ryoku mon-plugin "Mon plugin"
   ```

   Le dossier contient `AGENTS.md` : les règles R1–R11 que le validateur applique (R2 : tout fichier supplémentaire est listé dans `files`, R6 : commandes externes dans `dependencies.commands`, R8 : écriture seulement dans `stateDir`). Les noms de propriétés QML ne peuvent pas commencer par une majuscule ; le journal du shell est dans `/run/user/1000/quickshell/by-id/*/log.log`.
2. Écrire `service/Main.qml` (logique), `content/Widget.qml` (vue), `content/Panel.qml` (panneau de barre). Pour suivre le thème, utiliser les jetons de `Ryoku.PluginKit.Singletons` (`Theme`, `Motion`) et les composants du kit (`MicroLabel`), pas de couleur codée en dur.
3. **Scripts dans `bin/`** : la CI lance `shellcheck` sur `linux/*/*/bin/*`. Seuls des scripts shell (bash) y vont. Un script Python dans `bin/` fait échouer la CI (SC1071) : le placer dans `service/` sans shebang, listé dans `files`, et le lancer avec `python3 <chemin>` (`python3` dans `dependencies.commands`). Reproduire le contrôle sans installer shellcheck :

   ```bash
   python3 -m venv /tmp/sc && /tmp/sc/bin/pip install shellcheck-py
   /tmp/sc/bin/shellcheck scripts/*.sh linux/*/*/bin/*
   ```

4. Valider, puis essayer en local :

   ```bash
   ryoku plugin validate linux/ryoku/mon-plugin        # 0 blocage requis
   BASE_REF=origin/main scripts/validate-all.sh        # comme la CI
   ryoku plugin add linux/ryoku/mon-plugin --bar --yes
   ryoku plugin remove mon-plugin                      # avant de réinstaller une nouvelle version
   ```

5. Crédits : si le plugin dérive d'un autre travail, garder le copyright de l'auteur dans son `LICENSE`, ajouter une ligne à `CREDITS.md` et une section Credits au README du plugin.
6. Régénérer l'index (`scripts/gen-index.sh`) : `validate` échoue si la table du README et `plugins.json` sont périmés. Ne pas les éditer à la main.
7. Identité git : si git n'en a pas, la définir **dans le dépôt seulement** (`git config user.name` et `user.email`, par exemple l'adresse noreply GitHub), pas en global.
8. Committer, pousser la branche, ouvrir la PR :

   ```bash
   git add -A && git commit -m "mon-plugin : nouveau plugin Ryoku"
   git push -u origin feat/mon-plugin
   gh pr create --base main --head feat/mon-plugin
   ```

   Sur la PR, `validate` (plugins, dossiers supprimés, index, shellcheck) doit passer, `version` relève la version du manifest des plugins modifiés (patch par défaut ; étiquette `bump:minor` ou `bump:major` pour plus) et `mirror` tourne à blanc.
9. Publier : passer `status` de `draft` à `experimental` (ou `stable`) dans le manifest. **La fusion de la PR publie** : sur `main`, `mirror` crée `remi-deher/<id>` au premier passage, règle description, topics et « issues désactivées » d'après le manifest, pousse le dossier du plugin comme racine du miroir, pose le tag `v<version>` et les rulesets en lecture seule. Le workflow tourne aussi chaque jour. Fusion : `gh pr merge <n> --squash --delete-branch`.
10. Vérifier :

    ```bash
    gh repo view remi-deher/mon-plugin
    ryoku plugin remove mon-plugin
    ryoku plugin add https://github.com/remi-deher/mon-plugin --bar --yes
    ```

11. Catalogue officiel (seulement sur décision) : `ryoku plugin share mon-plugin`.

## Validation

- Chaîne complète faite pour `proton-vpn` : PR n°13, quatre contrôles verts (`validate` ×2, `version`, `mirror`), fusion en squash, miroir `remi-deher/proton-vpn` créé par la CI (description, tag `v0.1.0`), installation par URL réussie.
- Le miroir est créé et mis à jour sans intervention : aucune commande `gh repo create` ni `git subtree split` à lancer.
- Non validé : `scripts/new-plugin.sh`, `ryoku plugin share`.

## Pièges rencontrés

- Python dans `bin/` : échec de shellcheck en CI (voir l'étape 3).
- Un contenu de plugin modifié sans nouvelle version fait échouer `mirror` : un tag ne bouge jamais. `version` relève la version sur la PR ; ne la modifier à la main que pour un saut plus grand.
- Un miroir qui a divergé n'est jamais écrasé seul ; relancer le workflow `mirror` à la main avec `force` pour le réinitialiser.
- `rsync` peut manquer sur le poste : copier un dossier sans son `.git` avec `tar --exclude=.git -cf - . | tar -xf - -C <destination>`.
- `ryoku plugin new <id> --to ~/GitHub` a refusé (« already exists and is not empty ») ; avec `--to <nouveau-dossier>`, le plugin a été créé directement dans ce dossier. Comportement observé sur `~/GitHub/ryoku-proton-vpn`, non exploré davantage.
- Le secret `MIRROR_TOKEN` du dépôt doit exister, avec la permission Administration en plus de Contents (description, topics et rulesets du miroir) ; sans elle les étapes d'administration échouent avec un message explicite, mais le code du miroir est déjà à jour.

## Retour arrière

`ryoku plugin remove <id>`. Ne jamais supprimer le dossier d'un plugin publié : le garder avec `status: archived`, la CI archive alors le miroir. Pour un renommage, ajouter `"replaces": "<ancien-id>"` au manifest du nouveau plugin.

## Références

- [Fiche AirPods](../AIRPODS/README.md), exemple concret avec démon livré en source.
- Dépôts : [linux-plugins](https://github.com/remi-deher/linux-plugins), [ryoku-pods](https://github.com/remi-deher/ryoku-pods), [proton-vpn](https://github.com/remi-deher/proton-vpn) (portage d'OmaProton VPN, source de la procédure testée).
