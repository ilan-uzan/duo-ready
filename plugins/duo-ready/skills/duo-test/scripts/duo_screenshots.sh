#!/usr/bin/env bash
#
# duo_screenshots.sh — capture both iPhone Duo simulator displays as PNGs sized
# for App Store Connect, and print each file's pixel size.
#
# Output files (names fixed so they drop straight into an App Store Connect upload):
#   <out-dir>/outer-portrait-1398x2034.png   outer display, Apple's ASC size 1398x2034
#   <out-dir>/inner-portrait-2007x2853.png   inner display, Apple's ASC size 2007x2853
# Sizes come from Apple's App Store Connect screenshot specifications:
#   https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications
#
# IMPORTANT — the display identifiers are third-party, not Apple documentation.
#   Apple has not documented how `simctl io screenshot --display=` names the two
#   Duo displays. The defaults here (`primary` = outer, `primary-1` = inner) come
#   from a developer report of the Xcode 27.1 simulator (blakecrosley.com). A
#   different developer report (skarol.dev) saw `--display=1` for the outer
#   ("cover") display and `--display=3` for the inner one. This script therefore
#   prints the output of `xcrun simctl io <udid> enumerate` before capturing so
#   you can confirm the identifiers on your machine, and it lets you override
#   them with --outer-display / --inner-display. Always check the printed pixel
#   sizes against Apple's table above.
#
#   The simulator device type and runtime identifiers used when creating a
#   device (`com.apple.CoreSimulator.SimDeviceType.iPhone-Duo`,
#   `com.apple.CoreSimulator.SimRuntime.iOS-27-1`) are also third-party reports.
#   Confirm with `xcrun simctl list devicetypes` and `xcrun simctl list runtimes`.
#
# Known Apple issues this script cannot work around (Xcode 27.1 / 27.2 RC release notes):
#   187708500  Initial Simulator launch can take several minutes.
#   187146039  Screenshots and recordings in iPhone Duo might be black for up to a
#              few minutes after booting the device.
#   There is no `simctl` command to fold or open the device (Apple Developer
#   Forums thread 847883 has no Apple reply). Open the device in Xcode's Device
#   Hub (the Open button) before running this, or the inner capture will be of an
#   inactive display.
#
# Requires: macOS with Xcode 27.1 (27A9275) or later installed, `xcrun`, `sips`.
# This script was written without access to Xcode 27.1 and has only been
# syntax-checked; it is deliberately defensive and prints what it does.

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"

# Defaults (display identifiers: third-party, unverified; see header)
UDID=""
OUT_DIR="."
OUTER_DISPLAY="primary"
INNER_DISPLAY="primary-1"
CREATE_IF_MISSING=1
DEVICE_NAME="Duo-27.1"
DEVICE_TYPE="com.apple.CoreSimulator.SimDeviceType.iPhone-Duo"
RUNTIME="com.apple.CoreSimulator.SimRuntime.iOS-27-1"
SKIP_ENUMERATE=0

EXPECTED_OUTER="1398x2034"
EXPECTED_INNER="2007x2853"
OUTER_FILE="outer-portrait-${EXPECTED_OUTER}.png"
INNER_FILE="inner-portrait-${EXPECTED_INNER}.png"

usage() {
  cat <<USAGE
Usage: $SCRIPT_NAME [options] [UDID]

Capture both displays of an iPhone Duo simulator as PNG files named for App
Store Connect, then print each file's pixel size with sips.

Arguments:
  UDID                     Simulator UDID to use. If omitted, the script looks
                           for a booted iPhone Duo simulator, then any available
                           one, and otherwise creates "$DEVICE_NAME".

Options:
  --udid UDID              Same as the positional UDID.
  --out DIR                Output directory (default: current directory).
  --outer-display ID       simctl display id for the outer display
                           (default: $OUTER_DISPLAY; third-party, unverified).
  --inner-display ID       simctl display id for the inner display
                           (default: $INNER_DISPLAY; third-party, unverified).
  --no-create              Fail instead of creating a simulator when none exists.
  --device-name NAME       Name for a created simulator (default: $DEVICE_NAME).
  --device-type ID         Device type for creation (default: $DEVICE_TYPE).
  --runtime ID             Runtime for creation (default: $RUNTIME).
  --skip-enumerate         Do not print 'simctl io enumerate' output.
  -h, --help               Show this help.

Output files:
  DIR/$OUTER_FILE   (expect $EXPECTED_OUTER)
  DIR/$INNER_FILE   (expect $EXPECTED_INNER)

Before running: open the device in Xcode's Device Hub (Open button) so the inner
display is active. There is no simctl command to change the pose.

Exit codes: 0 both files captured at the expected sizes; 1 captured but at least
one size differs from Apple's table; 2 environment or usage error.
USAGE
}

die() { printf '%s: error: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 2; }
note() { printf '%s: %s\n' "$SCRIPT_NAME" "$*"; }

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --udid) [ $# -ge 2 ] || die "--udid needs a value"; UDID="$2"; shift 2 ;;
    --out) [ $# -ge 2 ] || die "--out needs a value"; OUT_DIR="$2"; shift 2 ;;
    --outer-display) [ $# -ge 2 ] || die "--outer-display needs a value"; OUTER_DISPLAY="$2"; shift 2 ;;
    --inner-display) [ $# -ge 2 ] || die "--inner-display needs a value"; INNER_DISPLAY="$2"; shift 2 ;;
    --no-create) CREATE_IF_MISSING=0; shift ;;
    --device-name) [ $# -ge 2 ] || die "--device-name needs a value"; DEVICE_NAME="$2"; shift 2 ;;
    --device-type) [ $# -ge 2 ] || die "--device-type needs a value"; DEVICE_TYPE="$2"; shift 2 ;;
    --runtime) [ $# -ge 2 ] || die "--runtime needs a value"; RUNTIME="$2"; shift 2 ;;
    --skip-enumerate) SKIP_ENUMERATE=1; shift ;;
    --) shift; break ;;
    -*) die "unknown option: $1 (try --help)" ;;
    *) [ -z "$UDID" ] || die "unexpected argument: $1"; UDID="$1"; shift ;;
  esac
done
[ $# -eq 0 ] || { [ -z "$UDID" ] || die "unexpected argument: $1"; UDID="$1"; }

# ---- environment checks -----------------------------------------------------

[ "$(uname -s)" = "Darwin" ] || die "this script needs macOS with Xcode installed (uname reports $(uname -s))"
command -v xcrun >/dev/null 2>&1 || die "xcrun not found. Install Xcode 27.1 (27A9275) or later and run: sudo xcode-select -s /Applications/Xcode.app"
command -v sips  >/dev/null 2>&1 || die "sips not found (it ships with macOS; check your PATH)"

if ! xcrun simctl help >/dev/null 2>&1; then
  die "'xcrun simctl' failed. Is Xcode selected? Check: xcode-select -p ; sudo xcode-select -s /Applications/Xcode.app"
fi

if command -v xcodebuild >/dev/null 2>&1; then
  note "toolchain: $(xcodebuild -version 2>/dev/null | tr '\n' ' ')"
  note "iPhone Duo support requires Xcode 27.1 (27A9275) or later; a 27.2 beta did not include it (third-party report)."
fi

mkdir -p "$OUT_DIR" || die "cannot create output directory: $OUT_DIR"

UDID_RE='[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}'

extract_udid() { grep -Eo "$UDID_RE" | head -n 1; }

# ---- find or create a device -------------------------------------------------

if [ -z "$UDID" ]; then
  note "no UDID given; looking for an iPhone Duo simulator"
  DUO_LINES="$(xcrun simctl list devices available 2>/dev/null | grep -i 'iPhone Duo' || true)"
  if [ -n "$DUO_LINES" ]; then
    BOOTED_LINE="$(printf '%s\n' "$DUO_LINES" | grep -i '(Booted)' | head -n 1 || true)"
    if [ -n "$BOOTED_LINE" ]; then
      UDID="$(printf '%s\n' "$BOOTED_LINE" | extract_udid)"
      note "using booted device: $(printf '%s' "$BOOTED_LINE" | sed 's/^[[:space:]]*//')"
    else
      UDID="$(printf '%s\n' "$DUO_LINES" | head -n 1 | extract_udid)"
      note "using device: $(printf '%s\n' "$DUO_LINES" | head -n 1 | sed 's/^[[:space:]]*//')"
    fi
  fi
  if [ -z "$UDID" ]; then
    if [ "$CREATE_IF_MISSING" -ne 1 ]; then
      die "no iPhone Duo simulator found and --no-create given. Add one in Xcode (Device Hub '+' > iPhone > iPhone Duo) or re-download the iOS 27.1 runtime (Xcode > Settings > Components)."
    fi
    note "no iPhone Duo simulator found; creating '$DEVICE_NAME'"
    note "device type: $DEVICE_TYPE  runtime: $RUNTIME  (identifiers are third-party reports; confirm with 'xcrun simctl list devicetypes' and 'xcrun simctl list runtimes')"
    if ! UDID="$(xcrun simctl create "$DEVICE_NAME" "$DEVICE_TYPE" "$RUNTIME" 2>&1 | extract_udid)" || [ -z "$UDID" ]; then
      printf '%s\n' "----- xcrun simctl list devicetypes | grep -i duo -----" >&2
      xcrun simctl list devicetypes 2>/dev/null | grep -i duo >&2 || printf '%s\n' "(no device type matching 'duo'; install the iOS 27.1 runtime: xcodebuild -downloadPlatform iOS)" >&2
      printf '%s\n' "----- xcrun simctl list runtimes -----" >&2
      xcrun simctl list runtimes >&2 || true
      die "simctl create failed. Pass the correct ids with --device-type / --runtime, or create the device in Xcode and pass its UDID."
    fi
    note "created $UDID"
  fi
fi

printf '%s' "$UDID" | grep -Eq "^$UDID_RE$" || die "'$UDID' does not look like a simulator UDID"

# ---- boot -------------------------------------------------------------------

STATE="$(xcrun simctl list devices 2>/dev/null | grep -F "$UDID" | sed -E 's/.*\(([A-Za-z ]+)\)[[:space:]]*$/\1/' || true)"
if [ "$STATE" != "Booted" ]; then
  note "booting $UDID (Apple known issue 187708500: the first launch can take several minutes)"
  if ! BOOT_OUT="$(xcrun simctl boot "$UDID" 2>&1)"; then
    case "$BOOT_OUT" in
      *"Unable to boot device in current state: Booted"*) : ;;
      *) die "simctl boot failed: $BOOT_OUT" ;;
    esac
  fi
  xcrun simctl bootstatus "$UDID" -b >/dev/null 2>&1 || note "warning: 'simctl bootstatus' did not report a clean boot; continuing"
fi
note "device $UDID is booted"
note "reminder: there is no simctl command to fold or open the device. Open it in Device Hub (Open button) before trusting the inner-display file."
note "reminder: Apple known issue 187146039: screenshots may be black for up to a few minutes after boot."

# ---- enumerate displays -----------------------------------------------------

if [ "$SKIP_ENUMERATE" -ne 1 ]; then
  note "displays reported by 'xcrun simctl io $UDID enumerate' (confirm that --outer-display=$OUTER_DISPLAY and --inner-display=$INNER_DISPLAY exist below):"
  if ! xcrun simctl io "$UDID" enumerate 2>&1 | sed 's/^/    /'; then
    note "warning: 'simctl io enumerate' failed; capturing anyway"
  fi
fi

# ---- capture ----------------------------------------------------------------

capture() {
  # $1 display id, $2 output path, $3 label
  local display="$1" out="$2" label="$3"
  note "capturing $label display (--display=$display) -> $out"
  if ! xcrun simctl io "$UDID" screenshot --type=png --display="$display" "$out"; then
    die "screenshot of the $label display failed with --display=$display. Compare the enumerate output above and pass the right id with --${label}-display."
  fi
  [ -s "$out" ] || die "screenshot of the $label display produced an empty file: $out"
}

OUTER_PATH="$OUT_DIR/$OUTER_FILE"
INNER_PATH="$OUT_DIR/$INNER_FILE"
capture "$OUTER_DISPLAY" "$OUTER_PATH" "outer"
capture "$INNER_DISPLAY" "$INNER_PATH" "inner"

# ---- measure ----------------------------------------------------------------

pixel_size() {
  # prints WxH using sips -g pixelWidth -g pixelHeight
  local f="$1" w h
  w="$(sips -g pixelWidth  "$f" 2>/dev/null | awk '/pixelWidth/  {print $2}')"
  h="$(sips -g pixelHeight "$f" 2>/dev/null | awk '/pixelHeight/ {print $2}')"
  [ -n "$w" ] && [ -n "$h" ] || die "sips could not read $f"
  printf '%sx%s' "$w" "$h"
}

STATUS=0
check() {
  # $1 path, $2 expected, $3 label, $4 landscape variant accepted by App Store Connect
  local f="$1" expected="$2" label="$3" landscape="$4" got
  got="$(pixel_size "$f")"
  printf '%s\n' "----- $f -----"
  sips -g pixelWidth -g pixelHeight "$f"
  if [ "$got" = "$expected" ]; then
    note "$label display: $got matches Apple's App Store Connect size $expected"
  elif [ "$got" = "$landscape" ]; then
    note "$label display: $got is Apple's landscape size ($landscape); the simulator was rotated. Rename the file before upload."
    STATUS=1
  else
    note "warning: $label display: $got does not match Apple's App Store Connect size $expected (or landscape $landscape). The display id may be wrong; compare the enumerate output and use --${label}-display."
    STATUS=1
  fi
}

check "$OUTER_PATH" "$EXPECTED_OUTER" "outer" "2034x1398"
check "$INNER_PATH" "$EXPECTED_INNER" "inner" "2853x2007"

note "done. Look at both files before uploading: a black inner image means the device was closed or was captured too soon after boot."
exit "$STATUS"
