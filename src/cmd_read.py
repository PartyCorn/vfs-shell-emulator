"""Команды чтения VFS: ls, cd, pwd, find, du, head."""
import fnmatch
import posixpath

from cmdutil import get_node, join_path, node_text, split_flags
from errors import ShellError

HEAD_DEFAULT = 10
UNIT_STEP = 1024
SIZE_UNITS = "BKMGT"
LS_FLAGS = "al"
DU_FLAGS = "ahs"


def _ls_entry(node, name, long_format):
    """Одна запись ls: имя или строка с типом и размером."""
    if not long_format:
        return name
    kind = "d" if node.is_dir else "-"
    return f"{kind} {node.size:>8} {name}"


def _ls_one(shell, path, flags, titled):
    """Листинг одного пути, для каталога с заголовком при titled."""
    node = get_node(shell, "ls", path)
    long_format = "l" in flags
    if not node.is_dir:
        return _ls_entry(node, path, long_format)
    names = sorted(node.children)
    if "a" not in flags:
        names = [n for n in names if not n.startswith(".")]
    items = [_ls_entry(node.children[n], n, long_format) for n in names]
    text = ("\n" if long_format else "  ").join(items)
    return f"{path}:\n{text}" if titled else text


def cmd_ls(shell, args):
    """ls [-a] [-l] [путь...]: содержимое каталога."""
    flags, paths = split_flags("ls", args, LS_FLAGS)
    titled = bool(paths[1:])
    blocks = []
    for path in paths or ["."]:
        try:
            blocks.append(_ls_one(shell, path, flags, titled))
        except ShellError as err:
            blocks.append(str(err))
    return ("\n\n" if titled else "\n").join(blocks)


def cmd_cd(shell, args):
    """cd [путь]: смена текущего каталога, без аргумента корень VFS."""
    if args[1:]:
        raise ShellError("cd: too many arguments")
    path = args[0] if args else "/"
    node = get_node(shell, "cd", path)
    if not node.is_dir:
        raise ShellError(f"cd: {path}: Not a directory")
    shell.cwd = shell.resolve(path)
    return ""


def cmd_pwd(shell, _args):
    """pwd: текущий каталог."""
    return shell.cwd_text()


def _parse_find(args):
    """Разбирает аргументы find: пути, -name и -type."""
    opts = {"-name": None, "-type": None}
    paths = []
    items = iter(args)
    for arg in items:
        if arg in opts:
            opts[arg] = next(items, None)
            if opts[arg] is None:
                raise ShellError(f"find: missing argument to `{arg}'")
        elif arg.startswith("-"):
            raise ShellError(f"find: unknown predicate `{arg}'")
        else:
            paths.append(arg)
    if opts["-type"] not in (None, "f", "d"):
        raise ShellError(f"find: Unknown argument to -type: {opts['-type']}")
    return paths or ["."], opts["-name"], opts["-type"]


def _walk(node, display):
    """Обход в глубину: пары (путь для вывода, узел)."""
    yield display, node
    if node.is_dir:
        for name in sorted(node.children):
            child = node.children[name]
            yield from _walk(child, join_path(display, name))


def _matches(node, display, pattern, kind):
    """Проверяет условия -type и -name для узла."""
    if kind and node.is_dir != (kind == "d"):
        return False
    if pattern is None:
        return True
    base = posixpath.basename(display.rstrip("/")) or display
    return fnmatch.fnmatchcase(base, pattern)


def cmd_find(shell, args):
    """find [путь...] [-name шаблон] [-type f|d]: поиск по дереву."""
    paths, pattern, kind = _parse_find(args)
    lines = []
    for path in paths:
        try:
            start = get_node(shell, "find", path)
        except ShellError as err:
            lines.append(str(err))
            continue
        for display, node in _walk(start, path):
            if _matches(node, display, pattern, kind):
                lines.append(display)
    return "\n".join(lines)


def human_size(size):
    """Размер в читаемом виде: 512B, 1.5K, 2.0M."""
    value = float(size)
    for unit in SIZE_UNITS[:-1]:
        if value < UNIT_STEP:
            break
        value /= UNIT_STEP
    else:
        unit = SIZE_UNITS[-1]
    digits = 0 if unit == "B" else 1
    return f"{value:.{digits}f}{unit}"


def _du_lines(node, display, flags):
    """Строки du: сначала вложенные каталоги, затем сам узел."""
    lines = []
    if node.is_dir and "s" not in flags:
        for name in sorted(node.children):
            child = node.children[name]
            if child.is_dir or "a" in flags:
                path = join_path(display, name)
                lines.extend(_du_lines(child, path, flags))
    shown = human_size(node.size) if "h" in flags else str(node.size)
    lines.append(f"{shown}\t{display}")
    return lines


def cmd_du(shell, args):
    """du [-a] [-h] [-s] [путь...]: размеры в байтах."""
    flags, paths = split_flags("du", args, DU_FLAGS)
    lines = []
    for path in paths or ["."]:
        try:
            node = get_node(shell, "du", path)
        except ShellError as err:
            lines.append(str(err))
            continue
        lines.extend(_du_lines(node, path, flags))
    return "\n".join(lines)


def _to_count(text):
    """Переводит значение -n в число строк."""
    if text is None or not (text.isascii() and text.isdigit()):
        raise ShellError(f"head: invalid number of lines: '{text}'")
    return int(text)


def _parse_head(args):
    """Разбирает аргументы head: число строк и список файлов."""
    count = HEAD_DEFAULT
    files = []
    items = iter(args)
    for arg in items:
        if arg == "-n":
            count = _to_count(next(items, None))
        elif arg.startswith("-n"):
            count = _to_count(arg[2:])
        elif arg.startswith("-") and arg != "-":
            raise ShellError(f"head: invalid option -- '{arg[1:]}'")
        else:
            files.append(arg)
    return count, files


def _head_one(shell, path, count):
    """Первые count строк одного файла."""
    node = get_node(shell, "head", path)
    if node.is_dir:
        raise ShellError(f"head: {path}: Is a directory")
    return "\n".join(node_text(node).splitlines()[:count])


def cmd_head(shell, args):
    """head [-n N] файл...: первые N строк (по умолчанию 10)."""
    count, files = _parse_head(args)
    if not files:
        raise ShellError("head: missing file operand")
    titled = bool(files[1:])
    blocks = []
    for path in files:
        try:
            text = _head_one(shell, path, count)
        except ShellError as err:
            blocks.append(str(err))
            continue
        blocks.append(f"==> {path} <==\n{text}" if titled else text)
    return ("\n\n" if titled else "\n").join(blocks)
