#!/usr/bin/env bash
# Open 1Password Quick Access on the current Niri workspace.
# 1Password shows its Quick Access window on a fixed workspace; bring it to the current one and focus it.
set -u
ws=$(niri msg --json workspaces | python3 -c 'import json,sys; print(next(w["idx"] for w in json.load(sys.stdin) if w["is_focused"]))')
/opt/1Password/1password --quick-access
for _ in 1 2 3 4 5 6 7 8 9 10; do
    sleep 0.15
    id=$(niri msg --json windows | python3 -c '
import json,sys
for w in json.load(sys.stdin):
    if w.get("app_id") == "com.onepassword.OnePassword" and w.get("is_floating"):
        print(w["id"]); break')
    if [ -n "${id:-}" ]; then
        niri msg action move-window-to-workspace --window-id "$id" --focus false "$ws"
        niri msg action focus-window --id "$id"
        exit 0
    fi
done
