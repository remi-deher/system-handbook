# Claude Code : la question de confiance du dossier revient à chaque lancement

- Résumé : l'approbation « I trust this folder » est enregistrée dossier par dossier dans `~/.claude.json` et ne semble pas retenue pour `~` ; mettre `hasTrustDialogAccepted` à `true` pour `~` supprime la question dans `~` et ses sous-dossiers.
- Statut : résolu (confirmé par l'utilisateur : la question ne revient plus) ; la cause exacte pour `~` reste une hypothèse.
- Date : 2026-11-13.
- Dernière vérification : 2026-11-13, Claude Code 2.1.323, noyau 7.3.4-arch1-1, Arch Linux.
- Portée : Claude Code CLI sous Linux, lancement dans le dossier personnel ou dans ses sous-dossiers.
- Environnements testés : Claude Code 2.1.323, Arch Linux, fish et bash ; aucune autre version ni distribution.
- Prérequis et exclusions : `python3`. Ne concerne pas les approbations d'outils ou de serveurs MCP, seulement la boîte « Quick safety check ».

## But ou problème

Au lancement de `claude`, la boîte « Quick safety check: Is this a project you created or one you trust? » s'affiche à chaque fois dans `~`. On voulait qu'elle ne s'affiche plus pour `~` ni pour ses sous-dossiers.

## Diagnostic

- L'état se lit dans `~/.claude.json`, clé `projects.<dossier>.hasTrustDialogAccepted`.
- Constat : `~` restait à `false` alors que les sous-dossiers déjà approuvés étaient à `true`. Un sous-dossier jamais approuvé posait la question une première fois, puis passait à `true` après réponse « Yes » : l'approbation est donc propre à chaque dossier, sans héritage d'un dossier vers ses enfants tant que le parent est à `false`.
- Hypothèse non vérifiée : Claude Code ne persiste pas la réponse quand le dossier de travail est `~`. Aucune documentation officielle n'a été consultée pour le confirmer.
- Le fichier peut être réécrit par une session `claude` ouverte : la valeur peut donc revenir à `false`.

## Procédure ou utilisation

Option sans modification : lancer `claude` depuis un sous-dossier (par exemple `~/GitHub`) et répondre « Yes » une fois.

Pour couvrir `~` (bash ; fermer les sessions `claude` avant) :

```bash
cp -p ~/.claude.json ~/.claude.json.bak-AAAA-MM-JJ
python3 -I - <<'PY'
import json, os, tempfile
p = os.path.expanduser('~/.claude.json')
d = json.load(open(p))
d['projects'][os.path.expanduser('~')]['hasTrustDialogAccepted'] = True
fd, t = tempfile.mkstemp(dir=os.path.dirname(p))
with os.fdopen(fd, 'w') as f:
    json.dump(d, f, indent=2)
os.chmod(t, 0o600)
os.replace(t, p)
PY
```

La clé `projects.<~>` doit déjà exister (créée par un premier lancement dans `~`) ; sinon le script échoue sans rien écrire.

## Validation

- Essai réel : `~/.claude.json` relu après modification (`~` à `true`), puis `claude` relancé dans `~` : la question n'est plus posée (confirmé par l'utilisateur).
- Limite : le test explicite d'un sous-dossier jamais approuvé, avec `~` à `true`, n'a pas été consigné séparément ; vérifier ce point avant de s'y fier.

## Persistance et maintenance

Une session `claude` ouverte peut réécrire `~/.claude.json` et remettre la valeur à `false` ; une mise à jour de Claude Code peut aussi changer ce comportement. Si la question revient, relire la valeur avant de chercher ailleurs. Le fichier contient d'autres données (projets, historique) : ne jamais le publier.

## Sauvegarde et retour arrière

Fermer `claude`, puis restaurer la sauvegarde : `cp -p ~/.claude.json.bak-AAAA-MM-JJ ~/.claude.json`.

## Références

- [setup-claude-remote-control](../05-SCRIPT/setup-claude-remote-control.md) : script archivé dont l'avertissement sur l'approbation de `~` est concerné.
