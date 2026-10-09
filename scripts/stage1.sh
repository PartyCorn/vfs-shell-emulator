#!/bin/sh
# Этап 1: REPL, переменные окружения, команды, ошибки.
. "$(dirname "$0")/common.sh"
export HOME=/home/user
export DEMO_VAR=world

emu --prompt "$ " <<'INPUT'
ls -l $HOME
cd ${DEMO_VAR}
ls "two words" '$HOME'
ls $UNDEFINED_VAR

foo bar
ls "unclosed
exit
INPUT
