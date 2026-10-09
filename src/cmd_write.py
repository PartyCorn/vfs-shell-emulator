"""Команды изменения VFS: touch и cp. Всё происходит только в памяти."""
from cmdutil import get_node, split_flags
from errors import ShellError, VfsError
from vfs import VNode

RECURSIVE_FLAGS = "rR"


def _touch_one(shell, path):
    """Создаёт пустой файл, если такого узла ещё нет."""
    parts = shell.resolve(path)
    if shell.vfs.find(parts) is None:
        shell.vfs.put(parts, VNode(parts[-1]))


def cmd_touch(shell, args):
    """touch файл...: создаёт пустые файлы, существующие не меняет."""
    _flags, paths = split_flags("touch", args, "")
    if not paths:
        raise ShellError("touch: missing file operand")
    errors = []
    for path in paths:
        try:
            _touch_one(shell, path)
        except VfsError as err:
            errors.append(f"touch: {path}: {err}")
    return "\n".join(errors)


def _copy_one(shell, src, dest_parts, into_dir, recursive):
    """Копирует один источник, при ошибке поднимает ShellError."""
    node = get_node(shell, "cp", src)
    if node.is_dir and not recursive:
        raise ShellError(f"cp: -r not specified; omitting directory '{src}'")
    src_parts = shell.resolve(src)
    target = dest_parts + src_parts[-1:] if into_dir else dest_parts
    shown = "/" + "/".join(target)
    if target == src_parts:
        raise ShellError(f"cp: '{src}' and '{shown}' are the same file")
    if node.is_dir and target[:len(src_parts)] == src_parts:
        raise ShellError(
            f"cp: cannot copy a directory, '{src}', into itself, '{shown}'"
        )
    try:
        shell.vfs.put(target, node)
    except VfsError as err:
        raise ShellError(
            f"cp: cannot copy '{src}' to '{shown}': {err}"
        ) from err


def cmd_cp(shell, args):
    """cp [-r] источник... назначение: копирование внутри VFS."""
    flags, rest = split_flags("cp", args, RECURSIVE_FLAGS)
    if not rest:
        raise ShellError("cp: missing file operand")
    if not rest[1:]:
        raise ShellError(
            f"cp: missing destination file operand after '{rest[0]}'"
        )
    sources, dest = rest[:-1], rest[-1]
    dest_parts = shell.resolve(dest)
    dest_node = shell.vfs.find(dest_parts)
    into_dir = dest_node is not None and dest_node.is_dir
    if sources[1:] and not into_dir:
        raise ShellError(f"cp: target '{dest}' is not a directory")
    errors = []
    for src in sources:
        try:
            _copy_one(shell, src, dest_parts, into_dir, bool(flags))
        except ShellError as err:
            errors.append(str(err))
    return "\n".join(errors)
