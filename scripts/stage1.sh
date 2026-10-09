#!/bin/sh
# Этап 1: REPL, переменные окружения, заглушки, ошибки.
. "$(dirname "$0")/common.sh"
export HOME=/home/user
export DEMO_VAR=world

emu <<'INPUT'
ls -l $HOME
cd ${DEMO_VAR} "two words" '$HOME'
ls $UNDEFINED_VAR end

foo bar
ls "unclosed
exit
INPUT
