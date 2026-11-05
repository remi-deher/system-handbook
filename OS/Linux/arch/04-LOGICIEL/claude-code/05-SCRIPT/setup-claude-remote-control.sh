#!/usr/bin/env bash
# Installe (ou met à jour) le service systemd utilisateur « claude-remote-control ».
# Idempotent : peut être relancé sans effet de bord. Portable : aucun nom de
# machine, d'utilisateur ou de chemin en dur (%h = $HOME, %H = nom d'hôte).
#
# Usage : setup-claude-remote-control [--name NOM]
#   --name NOM   nom de session fixé explicitement (sinon : nom de la machine)
set -euo pipefail

UNIT=claude-remote-control.service
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
ENV_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/claude-remote-control.env"

command -v claude >/dev/null || { echo "claude introuvable dans le PATH" >&2; exit 1; }

NAME=""
while [ $# -gt 0 ]; do
  case "$1" in
    --name) NAME="${2:?--name demande une valeur}"; shift 2 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "Option inconnue : $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$UNIT_DIR"

# Fichier d'environnement : créé une seule fois, jamais écrasé sauf avec --name.
# RC_NAME vide ou absent => nom de la machine (%H dans l'unité).
if [ -n "$NAME" ] || [ ! -e "$ENV_FILE" ]; then
  printf '# Nom de la session Remote Control (vide = nom de la machine)\nRC_NAME=%s\n' "$NAME" > "$ENV_FILE"
fi

# Le dossier ~ doit être approuvé (impossible à demander sans terminal).
if ! grep -q '"hasTrustDialogAccepted": *true' "$HOME/.claude.json" 2>/dev/null; then
  echo "Attention : lance une fois 'claude' dans ~ pour approuver le dossier." >&2
fi

TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
cat > "$TMP" <<EOF
[Unit]
Description=Claude Code Remote Control
Documentation=https://code.claude.com/docs
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=%h
Environment=PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin
Environment=RC_NAME=%H
# Un RC_NAME vide dans le fichier retombe sur le nom de la machine (voir ExecStart).
EnvironmentFile=-%E/claude-remote-control.env
# "y" automatique à la question « Enable Remote Control? » ; stdin reste ouvert ; bash (pas exec) quitte avec claude pour que systemd relance.
ExecStart=/bin/bash -c 'claude remote-control --name "\${RC_NAME:-\$(hostname)}" < <(echo y; exec sleep infinity)'
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

CHANGED=0
if ! cmp -s "$TMP" "$UNIT_DIR/$UNIT" 2>/dev/null || [ -n "$NAME" ]; then
  install -m 644 "$TMP" "$UNIT_DIR/$UNIT"; CHANGED=1
fi

# Démarrage au boot sans session ouverte.
if [ "$(loginctl show-user "$USER" -p Linger --value 2>/dev/null)" != yes ]; then
  loginctl enable-linger "$USER" || echo "Impossible d'activer le linger (à faire avec sudo)." >&2
fi

systemctl --user daemon-reload
systemctl --user enable "$UNIT" >/dev/null 2>&1
if [ "$CHANGED" = 1 ] || ! systemctl --user is-active --quiet "$UNIT"; then
  systemctl --user restart "$UNIT"
fi
sleep 5
systemctl --user --no-pager status "$UNIT" | sed -n '1,4p'
