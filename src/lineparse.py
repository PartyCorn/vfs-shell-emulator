"""Разбор строки: раскрытие переменных окружения и токенизация."""
import os
import re
import shlex

ENV_PATTERN = re.compile(r"'[^']*'|\$\{(\w+)\}|\$(\w+)")


class ParseError(Exception):
    """Строку невозможно разобрать, например не закрыта кавычка."""


def _substitute(match, env):
    """Заменяет одну переменную, участки в одинарных кавычках не трогает."""
    name = match.group(1) or match.group(2)
    if name is None:
        return match.group(0)
    return env.get(name, "")


def expand_env(line, env=None):
    """Раскрывает $VAR и ${VAR}, неизвестные переменные дают пустую строку."""
    env = os.environ if env is None else env
    return ENV_PATTERN.sub(lambda m: _substitute(m, env), line)


def parse_line(line, env=None):
    """Возвращает список токенов строки после раскрытия переменных."""
    try:
        return shlex.split(expand_env(line, env))
    except ValueError as err:
        raise ParseError(str(err)) from err
