#!/bin/sh
# Этап 5: touch и cp, проверка, что диск не изменился.
. "$(dirname "$0")/common.sh"

snapshot() {
    find examples | sort
    find examples -type f | sort | xargs cksum
}

before=$(snapshot)
echo "--- stage5.emu на VFS deep"
emu --vfs examples/deep --script scripts/startup/stage5.emu < /dev/null
echo "--- stage5_minimal.emu на VFS minimal"
emu --vfs examples/minimal --script scripts/startup/stage5_minimal.emu \
    --prompt "$ " < /dev/null
echo "--- каталог examples на диске до и после"
if [ "$before" = "$(snapshot)" ]; then
    echo "диск не изменён: OK"
else
    echo "диск изменён: ОШИБКА"
fi
