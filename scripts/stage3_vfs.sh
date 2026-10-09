#!/bin/sh
# Этап 3: разные варианты VFS и motd.
. "$(dirname "$0")/common.sh"

for vfs in minimal several deep; do
    echo "--- VFS $vfs"
    printf 'vfs-info\n' | emu --vfs "examples/$vfs"
done
echo "--- имя VFS в приглашении"
printf 'vfs-info\n' | emu --vfs examples/deep --prompt "[{vfs}] {cwd}> "
