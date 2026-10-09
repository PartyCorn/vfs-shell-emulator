"""Реестр команд эмулятора."""
from cmd_read import cmd_cd, cmd_du, cmd_find, cmd_head, cmd_ls, cmd_pwd


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


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "find": cmd_find,
    "du": cmd_du,
    "head": cmd_head,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}
