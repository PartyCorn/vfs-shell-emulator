#!/bin/sh
# Общие функции для демонстрационных скриптов.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

# emu ARGS: запуск эмулятора. По умолчанию консольный режим,
# с переменной EMU_GUI=1 открывается окно.
emu() {
    if [ -n "$EMU_GUI" ]; then
        python3 src/main.py "$@"
    elif [ -t 0 ]; then
        python3 src/main.py --headless "$@" < /dev/null
    else
        python3 src/main.py --headless "$@"
    fi
}
