#!/bin/sh
# Этап 3: ошибки загрузки VFS.
. "$(dirname "$0")/common.sh"

echo "--- каталога нет"
emu --vfs examples/missing < /dev/null
echo "exit code: $?"
echo "--- вместо каталога файл"
emu --vfs examples/several/readme.txt < /dev/null
echo "exit code: $?"
echo "--- без --vfs работает пустая VFS"
printf 'vfs-info\n' | emu
