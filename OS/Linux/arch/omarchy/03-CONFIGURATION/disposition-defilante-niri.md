# Disposition défilante inspirée de Niri

Résumé : configurer sous Omarchy la disposition défilante native de Hyprland, les gestes à trois doigts du pavé tactile et les raccourcis de fenêtres pour retrouver des éléments de l’expérience Niri ; la vue d’ensemble et les gestes à quatre doigts ont leurs propres fiches.

- Statut : configuration appliquée ; rechargement et options vérifiés, utilisation physique de la disposition, des gestes à trois doigts et des raccourcis à confirmer. La vue d’ensemble ([ScrollOverview](scrolloverview-hyprland.md)) et les [gestes à quatre doigts](gestes-vue-ensemble.md), confirmés par l’utilisateur, sont suivis dans leurs fiches.
- Date : 2026-11-11.
- Portée : Arch Linux, Omarchy et Hyprland ; ne configure pas Niri lui-même.
- Environnement observé : Omarchy 4.5.0-3, Hyprland 0.56.2 ; commandes en bash.
- Prérequis : pavé tactile pour les gestes ; `hyprpm` et le plugin tiers `scrolloverview` pour la vue d’ensemble. Les plugins Hyprland peuvent nécessiter une reconstruction après une mise à jour.

## Installation du plugin

Sur cette machine, `hyprpm` a été installé depuis les dépôts Arch. Le dépôt du plugin a été ajouté et le plugin activé :

```bash
omarchy pkg add hyprpm
hyprpm update
hyprpm add https://github.com/yayuuu/hyprland-scroll-overview.git
hyprpm enable scrolloverview
```

`hyprpm update` prépare les en-têtes nécessaires. Lors de l’installation observée, Hyprpm a choisi la révision du plugin correspondant à Hyprland 0.56.2 et l’a compilée. Les versions et la compatibilité peuvent évoluer.

## Configuration de Hyprland

Les extraits suivants décrivent les modifications dans les fichiers personnels, chargés après les valeurs Omarchy. Conserver les autres réglages existants et éviter de dupliquer les définitions.

Dans `~/.config/hypr/looknfeel.lua` :

```lua
hl.config({
  general = { gaps_in = 0, gaps_out = 0, border_size = 0, layout = "scrolling" },
  decoration = { rounding = 8 },
  scrolling = {
    column_width = 0.5,
    fullscreen_on_one_column = false,
    focus_fit_method = 1,
    explicit_column_widths = "0.5, 1.0",
    wrap_focus = false,
    wrap_swapcol = false,
  },
})

hl.curve("niriWorkspace", { type = "spring", mass = 1, stiffness = 1000, dampening = 63.25 })
hl.animation({ leaf = "workspaces", enabled = true, speed = 4, spring = "niriWorkspace", style = "slidevert" })
```

Les fenêtres n’ont ni marges ni bordures ; leurs coins restent arrondis. Les colonnes occupent par défaut la moitié de l’écran, même si une seule est présente. Les options du plugin ScrollOverview (échelle, fond, flou) et l’animation `windowsMove` qu’il utilise sont dans [la fiche ScrollOverview](scrolloverview-hyprland.md).

Dans `~/.config/hypr/input.lua` :

```lua
hl.config({ input = { touchpad = { natural_scroll = true } } })
hl.gesture({ fingers = 3, direction = "horizontal", action = "scroll_move" })
hl.gesture({ fingers = 3, direction = "vertical", action = "workspace" })
```

Le geste horizontal fait défiler les colonnes ; le geste vertical change d’espace de travail. Le sens et la sensation restent à vérifier sur le matériel utilisé. Les gestes à quatre doigts qui ouvrent et ferment la vue d’ensemble sont dans [leur fiche](gestes-vue-ensemble.md).

Dans `~/.config/hypr/bindings.lua` :

```lua
o.rebind("ALT + TAB", "Focus on next window", hl.dsp.window.cycle_next())
o.bind("ALT + TAB", "Reveal active window on top", hl.dsp.window.bring_to_top())
o.bind("CTRL + TAB", "Next workspace", hl.dsp.focus({ workspace = "m+1" }))
hl.unbind("SUPER + ALT + F")
o.bind("SUPER + D", "Cycle column width", hl.dsp.layout("colresize +conf"))
```

- `Super+Tab` ouvre la vue d’ensemble ScrollOverview (voir [sa fiche](scrolloverview-hyprland.md)) ; il passait auparavant à l’espace suivant.
- `Alt+Tab` parcourt les fenêtres de l’espace actif et met la fenêtre sélectionnée au premier plan ; `Alt+Maj+Tab` parcourt les fenêtres en sens inverse.
- `Ctrl+Tab` passe à l’espace suivant, action auparavant attribuée à `Alt+Tab`. Ce raccourci global intercepte aussi `Ctrl+Tab` dans les applications, notamment pour changer d’onglet.
- `Super+D` alterne la largeur de la colonne entre une demi-largeur et une largeur complète, sans passer la fenêtre en mode maximisé ; `Super+Alt+F` est désactivé. La largeur complète peut rester partiellement visible quand la vue défile vers une nouvelle colonne.
- `Super+Maj+Tab` conserve l’action Omarchy vers l’espace précédent.

Dans `~/.config/hypr/autostart.lua`, charger les plugins activés au démarrage de session :

```lua
o.exec_on_start("hyprpm reload -n")
```

## Vérification et retour arrière

```bash
hyprctl reload
hyprctl configerrors
hyprctl getoption general:layout
hyprctl getoption general:gaps_in
hyprctl getoption general:gaps_out
hyprctl getoption general:border_size
hyprpm list
hyprctl plugins list
```

Le 11 novembre 2026, le rechargement a été effectué sans erreur et la liste des raccourcis a confirmé les nouvelles affectations ; leur utilisation physique reste à vérifier. Le rechargement initial avait aussi été effectué sans erreur ; la disposition `scrolling`, le chargement du plugin et les raccourcis ont été vérifiés. Les marges et la bordure ont été vérifiées à zéro et les largeurs prédéfinies à 0,5 et 1,0 (l’échelle de la vue d’ensemble est suivie dans la fiche ScrollOverview). L’exécution physique des gestes à trois doigts et le scénario à deux fenêtres n’ont pas été vérifiés par l’agent ; le rechargement automatique du plugin à une nouvelle connexion reste à confirmer.

Pour revenir en arrière, retirer les extraits personnels concernés ou restaurer les fichiers `.bak.<horodatage>` appropriés après inspection ; recharger et vérifier les erreurs. `hyprpm disable scrolloverview` désactive le plugin si la vue d’ensemble n’est plus souhaitée. Une restauration complète Omarchy peut écraser d’autres préférences et n’est pas nécessaire.

## Références

- [Disposition défilante Hyprland](https://wiki.hypr.land/configuring/layouts/scrolling-layout/).
- [Gestes Hyprland](https://wiki.hypr.land/configuring/core/binds/gestures/).
- [ScrollOverview](https://github.com/yayuuu/hyprland-scroll-overview).
- Fiches liées : [vue des workspaces avec ScrollOverview](scrolloverview-hyprland.md), [gestes du pavé tactile pour la vue d’ensemble](gestes-vue-ensemble.md).
