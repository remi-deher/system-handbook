#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ASSET_DIR="$SCRIPT_DIR"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
BACKUP_DIR="$STATE_HOME/ryoku-latitude-audio/backups/$(date +%Y%m%d-%H%M%S)"
NIRI_BINDINGS="$CONFIG_HOME/niri/rebinds.kdl"
WIREPLUMBER_DIR="$CONFIG_HOME/wireplumber/wireplumber.conf.d"
LOCAL_BIN="$HOME/.local/bin"
AIRPODS_SINK=""
DRY_RUN=false
CHANGED_WIREPLUMBER=false
CHANGED_QUICKSHELL=false
ALSA_STORED=false

usage() {
	cat <<'EOF'
Usage: installer-audio-latitude-7440.sh [options]

Install the recorded Ryoku audio setup on a Dell Latitude 7440 with a Realtek
ALC289 codec. Run it as your desktop user, without sudo.

Options:
  --airpods-sink NAME  Set the exact PipeWire sink name for the AirPods profile.
  --dry-run            Show the actions without changing the system.
  -h, --help           Show this help.

If AirPods are connected, their sink is detected automatically. Otherwise, the
speaker profile is installed and the AirPods profile can be added by rerunning
the script with --airpods-sink after connecting them.
EOF
}

log() {
	printf '[audio-setup] %s\n' "$*"
}

warn() {
	printf '[audio-setup] AVERTISSEMENT : %s\n' "$*" >&2
}

die() {
	printf '[audio-setup] ERREUR : %s\n' "$*" >&2
	exit 1
}

as_root() {
	sudo "$@"
}

backup_target() {
	local target="$1"
	[[ -e "$target" ]] || return 0
	local saved="$BACKUP_DIR/${target#/}"
	mkdir -p -- "$(dirname -- "$saved")"
	cp -a -- "$target" "$saved"
	log "Sauvegarde : $target -> $saved"
}

install_file() {
	local source="$1"
	local target="$2"
	local mode="$3"
	local privileged="${4:-false}"

	if [[ -f "$target" ]] && cmp -s -- "$source" "$target"; then
		log "Déjà à jour : $target"
		return 0
	fi

	if [[ "$DRY_RUN" == true ]]; then
		log "Simulation : installation de $target"
		return 0
	fi
	backup_target "$target"
	if [[ "$privileged" == true ]]; then
		as_root install -D -m "$mode" -- "$source" "$target"
	else
		install -D -m "$mode" -- "$source" "$target"
	fi
	log "Installé : $target"
	if [[ "$target" == "$WIREPLUMBER_DIR/"* ]]; then
		CHANGED_WIREPLUMBER=true
	fi
	if [[ "$target" == "$CONFIG_HOME/ryoku/user_edits/quickshell/"* \
		|| "$target" == "$CONFIG_HOME/quickshell/"* ]]; then
		CHANGED_QUICKSHELL=true
	fi
}

set_mixer_baseline() {
	amixer -c PCH sset Speaker unmute || return 1
	amixer -c PCH sset Master 100% unmute || return 1
	amixer -c PCH sset 'Bass Speaker' 100% unmute || return 1
}

detect_airpods_sink() {
	command -v pw-dump >/dev/null 2>&1 || return 0
	command -v jq >/dev/null 2>&1 || return 0
	pw-dump 2>/dev/null | jq -r '
		.[]
		| select(.type == "PipeWire:Interface:Node")
		| .info.props as $p
		| select($p["media.class"] == "Audio/Sink")
		| select(($p["node.name"] // "") | startswith("bluez_output."))
		| select(([$p["device.description"] // "", $p["device.product.name"] // "", $p["device.nick"] // ""] | join(" ")) | test("AirPods"; "i"))
		| $p["node.name"]
	' | sort -u
}

patch_niri_volume_keys() {
	[[ -f "$NIRI_BINDINGS" ]] || {
		warn "${NIRI_BINDINGS} absent ; ajoutez les deux raccourcis indiqués dans le README."
		return 0
	}

	local raise_count lower_count
	raise_count="$(rg -c '^[[:space:]]*XF86AudioRaiseVolume([[:space:]]|$)' "$NIRI_BINDINGS" || true)"
	lower_count="$(rg -c '^[[:space:]]*XF86AudioLowerVolume([[:space:]]|$)' "$NIRI_BINDINGS" || true)"
	if [[ "$raise_count" != 1 || "$lower_count" != 1 ]]; then
		warn "raccourcis Niri absents ou ambigus ; je ne modifie pas $NIRI_BINDINGS."
		return 0
	fi

	local temporary
	temporary="$(mktemp)"
	while IFS= read -r line || [[ -n "$line" ]]; do
		if [[ "$line" == *XF86AudioRaiseVolume* ]]; then
			if [[ "$line" =~ ^([[:space:]]*XF86AudioRaiseVolume[^\{\}]*\{)[^\{\}]*(\}.*)$ ]]; then
				line="${BASH_REMATCH[1]} spawn \"ryoku-volume\" \"up\"; ${BASH_REMATCH[2]}"
			else
				rm -f -- "$temporary"
				warn "raccourci hausse sur plusieurs lignes ou format inconnu ; aucun changement Niri."
				return 0
			fi
		elif [[ "$line" == *XF86AudioLowerVolume* ]]; then
			if [[ "$line" =~ ^([[:space:]]*XF86AudioLowerVolume[^\{\}]*\{)[^\{\}]*(\}.*)$ ]]; then
				line="${BASH_REMATCH[1]} spawn \"ryoku-volume\" \"down\"; ${BASH_REMATCH[2]}"
			else
				rm -f -- "$temporary"
				warn "raccourci baisse sur plusieurs lignes ou format inconnu ; aucun changement Niri."
				return 0
			fi
		fi
	printf '%s\n' "$line" >> "$temporary"
	done < "$NIRI_BINDINGS"

	if ! rg -q 'XF86AudioRaiseVolume.*spawn "ryoku-volume" "up"' "$temporary" || \
	   ! rg -q 'XF86AudioLowerVolume.*spawn "ryoku-volume" "down"' "$temporary"; then
		rm -f -- "$temporary"
		warn "format des raccourcis non reconnu ; aucun changement Niri."
		return 0
	fi
	chmod --reference="$NIRI_BINDINGS" "$temporary"
	install_file "$temporary" "$NIRI_BINDINGS" "$(stat -c '%a' "$NIRI_BINDINGS")"
	rm -f -- "$temporary"
}

while (($#)); do
	case "$1" in
		--airpods-sink)
			(($# >= 2)) || die "--airpods-sink attend un nom de sink."
			AIRPODS_SINK="$2"
			shift 2
			;;
		--dry-run)
			DRY_RUN=true
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			die "option inconnue : $1"
			;;
	esac
done

[[ "$EUID" -ne 0 ]] || die "lancez le script comme utilisateur de bureau, sans sudo."
[[ -f "$ASSET_DIR/80-ryoku-audio-smart-filters.conf.in" ]] || die "fichiers assets introuvables à côté du script."
for asset in \
	quickshell-OsdFeed.qml \
	quickshell-OsdSource.qml \
	quickshell-PcmVolume.qml \
	quickshell-shell-audio-qmldir \
	quickshell-qsbar-AudioWidget.qml; do
	[[ -f "$ASSET_DIR/$asset" ]] || die "asset Quickshell manquant : $asset."
done

if [[ "$AIRPODS_SINK" != "" && ! "$AIRPODS_SINK" =~ ^bluez_output\.[A-Za-z0-9_.-]+$ ]]; then
	die "nom AirPods invalide : attendez-vous à bluez_output.<identifiant>.1."
fi

if [[ "$DRY_RUN" == false ]]; then
	command -v sudo >/dev/null 2>&1 || die "sudo est requis pour installer les paquets et le retask HDA."
fi

if [[ "$DRY_RUN" == false ]]; then
	[[ -r /etc/os-release ]] || die "impossible d'identifier la distribution."
	# shellcheck disable=SC1091
	source /etc/os-release
	[[ "${ID:-}" == arch || " ${ID_LIKE:-} " == *" arch "* ]] || die "ce script est prévu pour Arch Linux."
	[[ "$(cat /sys/class/dmi/id/product_name 2>/dev/null || true)" == *"Latitude 7440"* ]] || die "modèle détecté différent du Dell Latitude 7440."
	codec_match=false
	for codec_file in /proc/asound/card*/codec#*; do
		[[ -f "$codec_file" ]] || continue
		if grep -q 'Codec: Realtek ALC289' "$codec_file" && grep -q 'Subsystem Id: 0x10280c0c' "$codec_file"; then
			codec_match=true
			break
		fi
	done
	[[ "$codec_match" == true ]] || die "codec Realtek ALC289 avec le sous-identifiant Dell 0x10280c0c introuvable."
	command -v pacman >/dev/null 2>&1 || die "pacman est introuvable."

	packages=(pipewire pipewire-alsa pipewire-pulse wireplumber alsa-utils alsa-tools lsp-plugins-lv2 jq ripgrep)
	missing=()
	for package in "${packages[@]}"; do
		pacman -Qq "$package" >/dev/null 2>&1 || missing+=("$package")
	done
	if ((${#missing[@]})); then
		log "Installation des dépendances : ${missing[*]}"
		as_root pacman -S --needed "${missing[@]}"
	fi
	command -v rg >/dev/null 2>&1 || die "ripgrep reste introuvable après l'installation des dépendances."
	for required_command in amixer alsactl pactl wpctl pw-link; do
		command -v "$required_command" >/dev/null 2>&1 || die "commande requise absente : $required_command."
	done
	amixer -c PCH info >/dev/null 2>&1 || die "carte ALSA PCH introuvable."
	command -v qs >/dev/null 2>&1 || warn "qs introuvable ; les changements de volume fonctionneront, sans OSD Ryoku."
else
	log "Simulation : vérification du modèle, des paquets et du codec ignorée."
fi

if [[ -z "$AIRPODS_SINK" && "$DRY_RUN" == false ]]; then
	mapfile -t detected_airpods < <(detect_airpods_sink)
	if ((${#detected_airpods[@]} == 1)); then
		AIRPODS_SINK="${detected_airpods[0]}"
		log "Profil AirPods détecté : $AIRPODS_SINK"
	elif ((${#detected_airpods[@]} > 1)); then
		warn "plusieurs sinks AirPods détectés ; profil AirPods ignoré, passez --airpods-sink <nom>."
	else
		log "Aucun sink AirPods connecté ; installation du profil haut-parleurs seulement."
	fi
fi

if [[ "$DRY_RUN" == false ]]; then
	if ! systemctl --user enable --now pipewire.socket pipewire-pulse.socket wireplumber.service; then
		warn "impossible d'activer PipeWire dans cette session utilisateur."
	fi
fi

smart_filters="$(mktemp)"
if [[ -n "$AIRPODS_SINK" ]]; then
	sed "s|__RYOKU_AIRPODS_SINK__|$AIRPODS_SINK|g" \
		"$ASSET_DIR/80-ryoku-audio-smart-filters.conf.in" > "$smart_filters"
else
	sed \
		-e '/filter.sink.ryoku-airpods-smartfx = required/d' \
		-e '/# BEGIN RYOKU OPTIONAL AIRPODS PROFILE/,/# END RYOKU OPTIONAL AIRPODS PROFILE/d' \
		"$ASSET_DIR/80-ryoku-audio-smart-filters.conf.in" > "$smart_filters"
fi
trap 'rm -f -- "$smart_filters"' EXIT

install_file "$ASSET_DIR/51-ryoku-bluetooth.conf" "$WIREPLUMBER_DIR/51-ryoku-bluetooth.conf" 0644
install_file "$smart_filters" "$WIREPLUMBER_DIR/80-ryoku-audio-smart-filters.conf" 0644
install_file "$ASSET_DIR/ryoku-audio-output" "$LOCAL_BIN/ryoku-audio-output" 0755
install_file "$ASSET_DIR/ryoku-volume" "$LOCAL_BIN/ryoku-volume" 0755
install_file "$ASSET_DIR/quickshell-OsdFeed.qml" "$CONFIG_HOME/ryoku/user_edits/quickshell/shell/services/OsdFeed.qml" 0644
install_file "$ASSET_DIR/quickshell-OsdFeed.qml" "$CONFIG_HOME/quickshell/shell/services/OsdFeed.qml" 0644
install_file "$ASSET_DIR/quickshell-OsdSource.qml" "$CONFIG_HOME/ryoku/user_edits/quickshell/shell/modules/osd/OsdSource.qml" 0644
install_file "$ASSET_DIR/quickshell-OsdSource.qml" "$CONFIG_HOME/quickshell/shell/modules/osd/OsdSource.qml" 0644
install_file "$ASSET_DIR/quickshell-PcmVolume.qml" "$CONFIG_HOME/ryoku/user_edits/quickshell/shell/audio/PcmVolume.qml" 0644
install_file "$ASSET_DIR/quickshell-PcmVolume.qml" "$CONFIG_HOME/quickshell/shell/audio/PcmVolume.qml" 0644
install_file "$ASSET_DIR/quickshell-shell-audio-qmldir" "$CONFIG_HOME/ryoku/user_edits/quickshell/shell/audio/qmldir" 0644
install_file "$ASSET_DIR/quickshell-shell-audio-qmldir" "$CONFIG_HOME/quickshell/shell/audio/qmldir" 0644
install_file "$ASSET_DIR/quickshell-qsbar-AudioWidget.qml" "$CONFIG_HOME/ryoku/user_edits/quickshell/shell/modules/bar/barstyles/qsbar/modules/AudioWidget.qml" 0644
install_file "$ASSET_DIR/quickshell-qsbar-AudioWidget.qml" "$CONFIG_HOME/quickshell/shell/modules/bar/barstyles/qsbar/modules/AudioWidget.qml" 0644
patch_niri_volume_keys

if [[ "$DRY_RUN" == false ]]; then
	install_file "$ASSET_DIR/hda-jack-retask.conf" /etc/modprobe.d/hda-jack-retask.conf 0644 true
	install_file "$ASSET_DIR/hda-jack-retask.fw" /lib/firmware/hda-jack-retask.fw 0644 true

	log "Activation des interrupteurs Speaker et Bass Speaker, Master/Bass Speaker à 100 % ; PCM reste inchangé."
	if set_mixer_baseline; then
		backup_target /var/lib/alsa/asound.state
		as_root alsactl store PCH
		ALSA_STORED=true
	else
		warn "contrôle ALSA absent avant retask ; redémarrez puis relancez le script pour enregistrer Speaker/Master/Bass Speaker."
	fi

	if [[ "$CHANGED_WIREPLUMBER" == true ]]; then
		log "Redémarrage de WirePlumber pour charger les profils."
		systemctl --user restart wireplumber.service || warn "redémarrez manuellement WirePlumber."
	fi
	if [[ "$CHANGED_QUICKSHELL" == true ]]; then
		if command -v ryoku-shell >/dev/null 2>&1; then
			log "Rechargement de Quickshell pour appliquer les adaptations audio."
			ryoku-shell reload || warn "rechargez Quickshell manuellement pour appliquer les adaptations audio."
		else
			warn "ryoku-shell introuvable ; rechargez Quickshell après l'installation."
		fi
	fi
	if [[ "$ALSA_STORED" == true ]]; then
		log "Réglages ALSA enregistrés pour la prochaine session."
	fi
	log "Le retask de la broche 0x14 nécessite un redémarrage du PC."
else
	log "Simulation : installation des fichiers, ALSA, services et retask non exécutés."
fi

if [[ -d "$BACKUP_DIR" ]]; then
	log "Sauvegardes conservées dans : $BACKUP_DIR"
fi
log "Installation terminée. Redémarrez le PC avant de vérifier les deux étages de haut-parleurs."
