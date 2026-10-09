#!/bin/sh
# Этап 2: все параметры сразу и ошибки разбора параметров.
. "$(dirname "$0")/common.sh"
export HOME=/home/user

echo "--- все параметры"
emu --vfs examples/vfs_demo --prompt "vfs$ " \
    --script scripts/startup/basic.emu < /dev/null
echo "--- неизвестный параметр"
emu --unknown 2>&1 < /dev/null
echo "exit code: $?"
echo "--- параметр без значения"
emu --prompt 2>&1 < /dev/null
echo "exit code: $?"
