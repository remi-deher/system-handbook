# Vue des workspaces avec ScrollOverview

Résumé : configuration de ScrollOverview sous Omarchy et Hyprland pour afficher les workspaces avec Super+Tab, naviguer au clavier et corriger une erreur Lua de navigation.

- Statut : configuration chargée ; interaction et rendu à vérifier selon la session.
- Date : 2026-11-11.
- Portée : Omarchy, Hyprland et greffon ScrollOverview.
- Environnement observé : Hyprland 0.56.2, ScrollOverview `07a944e4d16f`, configuration Lua.
- Prérequis : greffon installé et activé avec `hyprpm`. Les options et API peuvent évoluer selon les versions.

## Configuration

Dans `~/.config/hypr/looknfeel.lua`, les options suivantes affichent le fond dans chaque aperçu et activent le flou de l’arrière-plan, sans ombre autour des aperçus :

```lua
hl.config({
  plugin = { scrolloverview = {
    scale = 0.7,
    wallpaper = 2,
    blur = true,
    shadow = { enabled = false },
  } },
})

-- ScrollOverview utilise l’animation de déplacement des fenêtres.
hl.animation({ leaf = "windowsMove", enabled = true, speed = 4.5, bezier = "easeOutQuint" })
```

Cette animation modifie également les déplacements de fenêtres hors aperçu. Le zoom spécifique du fond d’écran en arrière-plan n’est pas fourni par la version examinée.

Dans `~/.config/hypr/bindings.lua`, Super+Tab ouvre l’aperçu sur tous les écrans. Le sous-plan ci-dessous conserve la navigation, ferme l’aperçu avec Entrée, Échap ou Super+Tab sur la sélection clavier et crée un workspace vide en appuyant vers le bas depuis le dernier workspace occupé :

```lua
o.rebind("SUPER + TAB", "Workspace overview", function()
  hl.plugin.scrolloverview.overview("toggle all")
end)

local function overview_down()
  local monitor = hl.get_active_monitor()
  local active = monitor and monitor.active_workspace
  if active and type(active.id) == "number" and active.id > 0 and active.windows and active.windows > 0 then
    local last = active.id
    for _, workspace in ipairs(hl.get_workspaces()) do
      if workspace.monitor == monitor and not workspace.special and type(workspace.id) == "number" and workspace.id > last then
        last = workspace.id
      end
    end
    if active.id == last then
      hl.dispatch(hl.dsp.focus({ workspace = "emptynm" }))
      return
    end
  end
  hl.plugin.scrolloverview.navigate("down")
end

hl.define_submap("scrolloverview", function()
  hl.bind("left", hl.plugin.scrolloverview.navigate("left"))
  hl.bind("right", hl.plugin.scrolloverview.navigate("right"))
  hl.bind("up", hl.plugin.scrolloverview.navigate("up"))
  hl.bind("down", overview_down)
  hl.bind("return", hl.plugin.scrolloverview.overview("off"))
  hl.bind("KP_Enter", hl.plugin.scrolloverview.overview("off"))
  hl.bind("escape", hl.plugin.scrolloverview.overview("off"))
  hl.bind("SUPER + TAB", hl.plugin.scrolloverview.overview("off"))
  hl.bind("mouse:272", function()
    hl.plugin.scrolloverview.overview("select")
    hl.plugin.scrolloverview.window("select")
    hl.plugin.scrolloverview.overview("off")
  end, { mouse = true })
  hl.bind("mouse:274", hl.plugin.scrolloverview.window("close"), { mouse = true })
end)
```

`overview("select")` sélectionne le workspace sous le pointeur : l’utiliser pour Entrée peut donc sélectionner un autre workspace. La fermeture avec `off` conserve la sélection clavier. Un sous-plan personnalisé remplace les raccourcis habituels du greffon dans la vue ; adapter les raccourcis supplémentaires si nécessaire. La création utilise l’écran actif et le dernier identifiant existant sur cet écran ; les cas multi-écrans et les workspaces nommés ne sont pas validés.

## Erreur Lua et validation

L’erreur `hl.dispatch: expected a dispatcher` à la ligne de navigation provenait de `hl.dispatch(hl.plugin.scrolloverview.navigate("down"))`. Dans une fonction Lua, appeler directement `hl.plugin.scrolloverview.navigate("down")` ; les actions Hyprland `hl.dsp.*` restent utilisables avec `hl.dispatch`.

En shell Bash, après modification :

```bash
hyprctl reload
hyprctl configerrors
```

Le rechargement a réussi sans erreur de configuration et l’appel direct de navigation a été exécuté sans erreur. Le 11 novembre 2026, après ajout de Super+Tab au sous-plan, le rechargement a de nouveau réussi et `hyprctl binds -j` a confirmé son enregistrement ; son utilisation au clavier reste à vérifier. Le rendu de l’aperçu convient à l’utilisateur ; la sélection par Entrée et la création par la flèche bas après correction n’ont pas fait l’objet d’une confirmation explicite. Vérifier ces interactions en session et réexaminer la compatibilité après mise à jour de Hyprland ou du greffon.

## Retour arrière et références

Retirer les options et raccourcis ajoutés ou restaurer les copies locales des fichiers, puis recharger Hyprland. Sur la machine examinée, les copies initiales portent le suffixe `.bak.scrolloverview`.

- [Documentation des actions ScrollOverview](https://github.com/yayuuu/hyprland-scroll-overview/wiki/Dispatchers)
- [Sous-plan de raccourcis ScrollOverview](https://github.com/yayuuu/hyprland-scroll-overview/wiki/Keybind-submap)
- [Workspaces dynamiques](https://github.com/yayuuu/hyprland-scroll-overview/wiki/Dynamic-workspaces)
