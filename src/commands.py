"""Реестр команд эмулятора."""
from cmd_read import cmd_cd, cmd_du, cmd_find, cmd_head, cmd_ls, cmd_pwd
from cmd_write import cmd_cp, cmd_touch
from errors import ShellError


def cmd_exit(shell, _args):
    """Завершает работу эмулятора."""
    shell.running = False
    return ""


def cmd_vfs_info(shell, _args):
    """Служебная команда: сводка о загруженной VFS."""
    vfs = shell.vfs
    info = vfs.stats()
    return "\n".join([
        f"name: {vfs.name}",
        f"source: {vfs.source or '<память>'}",
        f"dirs: {info['dirs']}",
        f"files: {info['files']}",
        f"size: {info['size']} bytes",
        f"depth: {info['depth']}",
    ])


HELP = {
    "ls": "ls [-a] [-l] [путь...]  содержимое каталога",
    "cd": "cd [путь]  сменить каталог, без аргумента корень",
    "pwd": "pwd  текущий каталог",
    "find": "find [путь...] [-name шаблон] [-type f|d]  поиск",
    "du": "du [-a] [-h] [-s] [путь...]  размеры в байтах",
    "head": "head [-n N] файл...  первые N строк (по умолчанию 10)",
    "touch": "touch файл...  создать пустые файлы",
    "cp": "cp [-r] источник... назначение  копирование",
    "vfs-info": "vfs-info  сводка о загруженной VFS",
    "help": "help [команда]  справка по командам",
    "exit": "exit  завершить работу",
}


def cmd_help(_shell, args):
    """help [команда]: список команд или справка по одной."""
    if not args:
        return "\n".join(HELP[name] for name in HELP)
    if args[0] not in HELP:
        raise ShellError(f"help: no help for '{args[0]}'")
    return HELP[args[0]]


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "find": cmd_find,
    "du": cmd_du,
    "touch": cmd_touch,
    "cp": cmd_cp,
    "head": cmd_head,
    "help": cmd_help,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}
