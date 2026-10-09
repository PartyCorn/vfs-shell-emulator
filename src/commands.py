"""Команды эмулятора."""


def make_stub(name):
    """Создаёт команду-заглушку, которая печатает своё имя и аргументы."""
    def run(_shell, args):
        """Выводит имя команды и список аргументов."""
        return f"{name}: args={args}"
    return run


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
    "ls": make_stub("ls"),
    "cd": make_stub("cd"),
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}
