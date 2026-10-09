#!/bin/sh
# Этап 4: все команды этапов 1-4 на разных VFS.
. "$(dirname "$0")/common.sh"
export HOME=/home/user

echo "--- all_commands.emu на VFS deep"
emu --vfs examples/deep --script scripts/startup/all_commands.emu \
    --prompt "{vfs}:{cwd}$ " < /dev/null
echo "--- head_ls.emu на VFS several"
emu --vfs examples/several --script scripts/startup/head_ls.emu \
    --prompt "$ " < /dev/null
