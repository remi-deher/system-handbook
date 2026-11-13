#!/usr/bin/env bash
# Brightness up/down for both the laptop panel and external monitors.
#
#   ryoku-cmd-brightness +5   raise 5%
#   ryoku-cmd-brightness -5   lower 5%
#
# The laptop backlight goes through brightnessctl (/sys/class/backlight);
# external desktop monitors go through DDC/CI (ddcutil setvcp 10). Both run so a
# laptop docked to an external screen dims everything at once.
set -euo pipefail

delta=${1:?usage: ryoku-cmd-brightness <+N|-N>}
sign=${delta:0:1}
mag=${delta#[-+]}

case "$sign" in
  +|-) ;;
  *) echo "usage: ryoku-cmd-brightness <+N|-N>" >&2; exit 2 ;;
esac

# Laptop panel: only if a backlight device is present. Pin the panel's real
# backlight -- on ASUS AMD+NVIDIA laptops brightnessctl's default pick is the
# unreliable nvidia_wmi_ec_backlight, so ryoku-hw-backlight names the right one.
if compgen -G "/sys/class/backlight/*" >/dev/null; then
  device=$(ryoku-hw-backlight 2>/dev/null || true)
  (
    flock -x 9
    maximum=$(brightnessctl ${device:+-d "$device"} max)
    current=$(brightnessctl ${device:+-d "$device"} get)
    minimum=$(( (maximum + 99) / 100 ))
    threshold=$(( (maximum * 5 + 99) / 100 ))
    if (( current <= threshold )); then
      step=$minimum
    else
      step=$(( (maximum * mag + 99) / 100 ))
    fi
    if [[ $sign == "+" ]]; then
      if (( current < threshold )); then
        target=$(( current + step ))
      else
        # At or above 5%, resume at the next multiple of 5%.
        current_pct=$(( current * 100 / maximum ))
        next_pct=$(( (current_pct / 5 + 1) * 5 ))
        target=$(( (maximum * next_pct + 99) / 100 ))
      fi
      (( target > maximum )) && target=$maximum
    else
      target=$(( current - step ))
      if (( current > threshold && target < threshold )); then target=$threshold; fi
      (( target < minimum )) && target=$minimum
    fi
    brightnessctl ${device:+-d "$device"} --min-value="$minimum" set "$target" >/dev/null 2>&1 || true
  ) 9>"${XDG_RUNTIME_DIR:-/tmp}/ryoku-brightness-min.lock"
fi

# External monitors over DDC/CI. Only when a non-panel connector is actually
# connected: `ddcutil detect` walks every i2c bus (28 on a hybrid laptop, over
# 11s cold), and i2c traffic on the display controller is what froze the whole
# session on a brightness keypress (#176) -- the same stall 755ed028 gated out
# of the sidebar but not out of this key handler. The connector check is a
# sysfs file read, so it never touches i2c.
if command -v ddcutil >/dev/null 2>&1; then
  externals=()
  for c in "${RYOKU_DRM_PATH:-/sys/class/drm}"/*-*; do
    case "${c##*/}" in *eDP*|*LVDS*|*DSI*|*Writeback*) continue ;; esac
    [[ "$(cat "$c/status" 2>/dev/null)" == connected ]] && externals+=("${c##*/}")
  done
  if (( ${#externals[@]} )); then
    # Cache the detected buses under a key of the connected-external set, so a
    # docked user's repeated presses reuse the bus list instead of re-walking
    # every bus each time. Plugging in or out changes the key, so the cache
    # refreshes exactly on hotplug; it lives in the runtime dir, so a logout
    # clears it too.
    cache_dir="${XDG_RUNTIME_DIR:-/tmp}/ryoku-brightness-ddc"
    key="$(printf '%s\n' "${externals[@]}" | LC_ALL=C sort | tr -d '\n')"
    cache="$cache_dir/$(printf '%s' "$key" | cksum | cut -d' ' -f1)"
    mkdir -p "$cache_dir" 2>/dev/null || true
    if [[ -f $cache ]]; then
      mapfile -t buses <"$cache"
    else
      mapfile -t buses < <(ddcutil detect --brief 2>/dev/null | sed -n 's|.*/dev/i2c-\([0-9]\+\).*|\1|p')
      printf '%s\n' "${buses[@]}" >"$cache" 2>/dev/null || true
    fi
    lock="$cache_dir/lock"
    (
      flock -n 9 || exit 0
      for bus in "${buses[@]}"; do
        [[ -n $bus ]] || continue
        ddcutil --bus "$bus" --noverify setvcp 10 "$sign" "$mag" >/dev/null 2>&1 &
      done
      wait
    ) 9>"$lock" || true
  fi
fi
