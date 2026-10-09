#!/bin/sh
# Этап 3: общий стартовый скрипт на разных VFS.
. "$(dirname "$0")/common.sh"
export HOME=/home/user

for vfs in minimal deep; do
    echo "--- all_commands.emu на VFS $vfs"
    emu --vfs "examples/$vfs" --script scripts/startup/all_commands.emu \
        < /dev/null
done
