"""Общие помощники для команд."""
from errors import ShellError, VfsError


def get_node(shell, cmd, path):
    """Находит узел по пути пользователя или поднимает ShellError."""
    try:
        return shell.vfs.get(shell.resolve(path))
    except VfsError as err:
        raise ShellError(f"{cmd}: {path}: {err}") from err


def join_path(base, name):
    """Склеивает путь и имя: ('.', 'a') -> './a', ('/', 'a') -> '/a'."""
    return base.rstrip("/") + "/" + name


def node_text(node):
    """Содержимое файла как текст."""
    return node.data.decode("utf-8", errors="replace")


def _check_letters(cmd, letters, allowed):
    """Проверяет буквы флагов и возвращает их множеством."""
    for letter in letters:
        if letter not in allowed:
            raise ShellError(f"{cmd}: invalid option -- '{letter}'")
    return set(letters)


def split_flags(cmd, args, allowed):
    """Отделяет короткие флаги (-l, -la) от остальных аргументов."""
    flags = set()
    rest = []
    for pos, arg in enumerate(args):
        if arg == "--":
            rest.extend(args[pos + 1:])
            break
        if arg.startswith("-") and arg != "-":
            flags |= _check_letters(cmd, arg[1:], allowed)
        else:
            rest.append(arg)
    return flags, rest
