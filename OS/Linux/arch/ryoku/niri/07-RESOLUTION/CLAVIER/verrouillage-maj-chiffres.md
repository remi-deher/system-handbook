# Verr. Maj. et chiffres sur un clavier AZERTY

Résumé : sous Ryoku et Niri avec la disposition française, l'option XKB `caps:shiftlock` permet de saisir les chiffres de la rangée supérieure avec Verr. Maj. activé.

- Statut : testé (configuration et compilation XKB validées ; frappe physique à confirmer).
- Date : 2026-11-25.
- Dernière vérification : 2026-11-25 ; noyau 7.3.4-arch1-2, Niri 26.04-1, Ryoku Hub 1:1.1.0.r6233.g0bf1174-1, xkeyboard-config 2.49-1.
- Portée : Arch Linux, Ryoku, Niri, clavier AZERTY français.
- Environnement testé : session Niri, disposition XKB `fr`, shell Bash ; frappe physique non vérifiée.

## Problème et diagnostic

Avec la disposition `fr` et aucune option XKB, Verr. Maj. verrouille les majuscules mais ne transforme pas nécessairement les touches accentuées de la rangée supérieure en chiffres. Par exemple, la touche `é` ne produit pas `2` comme avec Maj. Ce comportement dépend de la disposition et de ses options.

## Réglage

Dans **Ryoku Hub → Input → Key Remaps → Extra options**, ajouter `caps:shiftlock` aux options XKB, séparé par une virgule des éventuelles options existantes, puis appliquer. Le Hub s'ouvre avec `Super` + `,`. Sur la machine testée, les options étaient initialement vides. Le Hub écrit la configuration Niri générée : ne pas modifier `settings.kdl` à la main.

Cette option transforme Verr. Maj. en verrouillage de Maj pour toutes les touches, y compris la ponctuation ; elle peut donc modifier des raccourcis. Tester les usages habituels. Elle concerne la session graphique ; l'écran de connexion et les consoles ne sont pas vérifiés.

## Validation

Le Hub indiquait `caps:shiftlock` et la configuration générée comportait cette option. `niri validate -c ~/.config/niri/config.kdl` a réussi et `xkbcli compile-keymap --layout fr --options caps:shiftlock` a compilé une disposition où la touche `é` possède `2` au niveau Maj et Verr. Maj. produit `Shift_Lock`. Ces contrôles ne remplacent pas un essai de frappe réel.

## Retour arrière

Dans **Input → Key Remaps → Extra options**, retirer uniquement `caps:shiftlock`, conserver les autres options et appliquer. La valeur précédente sur la machine testée était vide.

## Référence

- [Raccourcis AZERTY sous Niri](raccourcis-azerty.md), pour les raccourcis utilisant la rangée supérieure.
