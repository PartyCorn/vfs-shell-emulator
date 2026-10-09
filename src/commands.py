"""Команды эмулятора: на первом этапе заглушки и exit."""


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


COMMANDS = {
    "ls": make_stub("ls"),
    "cd": make_stub("cd"),
    "exit": cmd_exit,
}
