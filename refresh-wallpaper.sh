#!/usr/bin/env bash
# Regenerate the Lily58 wallpaper (refreshes the OpenRouter spend figure in the
# footer). Behaves identically to the daily lily58-wallpaper.service: regenerate
# the PNG, then re-assert picture-uri. GNOME's file monitor repaints the desktop
# when the PNG is overwritten. Shared by the meeting-transcribe hook so a
# post-meeting refresh works the same way as the daily one.
#
# No forced toggle: re-setting picture-uri to the same value is flash-free. If
# the live figure ever looks stale (file-monitor not repainting), this is the
# one place to add a forced reload.
#
# Generator failure -> exit 1 (visible in `systemctl --user status`); callers
# that must not be blocked append `|| true`.
set -uo pipefail

REPO="/home/b_bondar/dev/zmk-for-keyboards"
OUT="/home/b_bondar/Pictures/lily58_wallpaper.png"
PY=/usr/bin/python3   # has Pillow; independent of asdf/PATH under systemd

# Regenerate (network-optional: the generator drops the spend line if OpenRouter
# is unreachable, so this still succeeds offline).
"$PY" "$REPO/make_wallpaper.py" || { echo "refresh-wallpaper: generator failed" >&2; exit 1; }

# Re-assert the wallpaper URI. Needs the session bus; fall back to the well-known
# per-user bus path when run from a context that didn't inherit it.
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/bus}"
if command -v gsettings >/dev/null 2>&1; then
  uri="file://$OUT"
  gsettings set org.gnome.desktop.background picture-uri "$uri" 2>/dev/null || true
  gsettings set org.gnome.desktop.background picture-uri-dark "$uri" 2>/dev/null || true
fi
