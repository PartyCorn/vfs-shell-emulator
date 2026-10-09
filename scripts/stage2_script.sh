#!/bin/sh
# Этап 2: параметр --script, ошибочные строки, exit внутри скрипта.
. "$(dirname "$0")/common.sh"
export HOME=/home/user

echo "--- стартовый скрипт с ошибочными строками"
emu --script scripts/startup/basic.emu < /dev/null
echo "--- exit в середине скрипта"
emu --script scripts/startup/exit_midway.emu --prompt "> " < /dev/null
echo "--- несуществующий скрипт"
emu --script scripts/startup/missing.emu < /dev/null
