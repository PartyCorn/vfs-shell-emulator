#!/bin/sh
# Этап 2: параметр --prompt и отладочный вывод.
. "$(dirname "$0")/common.sh"
export HOME=/home/user

echo "--- без параметров"
printf 'ls\nexit\n' | emu
echo "--- свой prompt"
printf 'ls\nexit\n' | emu --prompt "emu> "
echo "--- prompt с пробелами и символами"
printf 'cd x\nexit\n' | emu --prompt "[user@host ~]# "
