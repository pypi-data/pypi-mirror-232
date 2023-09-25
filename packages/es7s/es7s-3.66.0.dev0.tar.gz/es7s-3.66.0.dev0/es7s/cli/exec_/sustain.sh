#!/bin/bash
#-------------------------------------------------------------------------------
# es7s/core
# (c) 2023 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------
__SELF="$(basename "$0" | sed -Ee 's/\..+$//')"
__USAGE="$(cat <<-EOL
Endlessly run the specified COMMAND with ARGS, keep track of launch count and
latest exit code.

Usage:
    ${__SELF} [COMMAND [ARGS...]]
EOL
)"

__now() { date $'+\e[2m%_e-%b-%y\e[22;33m %T\e[39m' ; }
__exit() { printf "\x1b[2J\x1b[H" ; exit ; }
__main () {
    trap __exit INT

    local restarts=0
    [[ $# -lt 1 ]] && set last -n$(($(tput lines)-5))

    while true ; do
        printf "\x1b[2J\x1b[H"
        "$@"

        local retcode=$?
        echo "Process exited with code $retcode"

        local cmd="$*"
        local totallen=$(( 22 + ${#cmd} + ${#restarts} ))
        printf "\x1b[H\x1b[9999G\x1b[${totallen}D\x1b[90;2m%s \x1b[34;22;1;48;5;17m %d \x1b[22;34;48;5;16m %s \x1b[m" \
                "$cmd" "$restarts" "$(__now)"

        sleep 1
        ((restarts++))
    done
}

[[ $* =~ (--)?help ]] && echo "$__USAGE" && exit
__main "$@"
