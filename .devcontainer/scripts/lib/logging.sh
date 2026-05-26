# =============================================
# Shared logging utilities for devcontainer scripts
# =============================================

# Color support detection (respects NO_COLOR and dumb terminals)
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ] && [ "${TERM:-}" != "dumb" ]; then
    COLOR_RESET='\033[0m'
    COLOR_RED='\033[0;31m'
    COLOR_GREEN='\033[0;32m'
    COLOR_YELLOW='\033[0;33m'
    COLOR_CYAN='\033[0;36m'
    COLOR_BOLD='\033[1m'
else
    COLOR_RESET=''
    COLOR_RED=''
    COLOR_GREEN=''
    COLOR_YELLOW=''
    COLOR_CYAN=''
    COLOR_BOLD=''
fi

# =============================================
# LOG_LEVEL support (DEBUG, INFO, WARN, ERROR)
# =============================================

# Normalize LOG_LEVEL (default: INFO)
_log_level_raw="${LOG_LEVEL:-INFO}"
_log_level=$(printf '%s' "$_log_level_raw" | tr '[:lower:]' '[:upper:]')

# Map level names to numeric values (lower number = more verbose)
case "$_log_level" in
    DEBUG)  CURRENT_LOG_LEVEL=0 ;;
    INFO)   CURRENT_LOG_LEVEL=1 ;;
    WARN|WARNING) CURRENT_LOG_LEVEL=2 ;;
    ERROR)  CURRENT_LOG_LEVEL=3 ;;
    *)      CURRENT_LOG_LEVEL=1 ;;   # default to INFO for unknown values
esac

# Internal log function with level filtering
_log() {
    local msg_level="$1"
    local color="$2"
    local prefix="$3"
    shift 3

    local msg_level_num
    case "$msg_level" in
        DEBUG)  msg_level_num=0 ;;
        INFO)   msg_level_num=1 ;;
        WARN)   msg_level_num=2 ;;
        ERROR)  msg_level_num=3 ;;
        *)      msg_level_num=1 ;;
    esac

    if [ "$msg_level_num" -lt "$CURRENT_LOG_LEVEL" ]; then
        return 0
    fi

    printf "${color}[%s]${COLOR_RESET} %s\n" "$prefix" "$*"
}

# Public logging functions
log_debug() {
    _log "DEBUG" "$COLOR_CYAN" "$1" "${@:2}"
}

log_info() {
    _log "INFO" "$COLOR_CYAN" "$1" "${@:2}"
}

log_success() {
    _log "INFO" "$COLOR_GREEN" "$1" "${@:2}"
}

log_warn() {
    _log "WARN" "$COLOR_YELLOW" "$1" "${@:2}"
}

log_error() {
    _log "ERROR" "$COLOR_RED" "$1" "${@:2}"
}
