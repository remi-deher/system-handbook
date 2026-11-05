# Clavier et raccourcis — Niri sous Ryoku

Catégorie des résolutions du clavier, de la disposition et des raccourcis. Une fiche Markdown par problème.

## Où chercher

- [raccourcis-azerty.md](raccourcis-azerty.md)
- [azerty-niri-user.kdl](azerty-niri-user.kdl)
- [ryoku-capture-azerty.patch](ryoku-capture-azerty.patch)

Voir les [instructions IA](00-AGENTS.md) et [l’index parent](../README.md).

## Résolution AZERTY à préserver

La fiche `raccourcis-azerty.md` décrit une résolution confirmée par l’utilisateur le 4 novembre 2026. Les noms XKB de la rangée française sont nécessaires pour Niri 26.04. Super+Alt déplace et suit la fenêtre ; Super+Maj déplace sans suivre (`focus=false`). La capture dans Ryoku et la génération/exécution Niri sont deux problèmes distincts. Les raccourcis personnels dans `user.kdl` doivent être adaptés si les réattributions du Hub changent. Le patch de capture ne corrige pas à lui seul toutes les familles générées.
