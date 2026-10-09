"""Точка входа эмулятора."""
import os
import sys

from config import parse_args
from session import Session
from shell import Shell


def run_console(session):
    """Консольный цикл: читает строки со стандартного ввода."""
    session.start()
    while session.shell.running:
        try:
            line = input(session.prompt_text())
        except EOFError:
            print()
            break
        if not sys.stdin.isatty():
            print(line)
        session.submit(line, echo=False)


def vfs_name(config):
    """Имя VFS для заголовка: имя каталога из --vfs или vfs."""
    if config.vfs:
        return os.path.basename(config.vfs.rstrip("/")) or "vfs"
    return "vfs"


def run_gui(shell, config):
    """Запускает графический интерфейс."""
    from gui import EmulatorWindow

    def make_session(emit):
        """Создаёт сессию с выводом в окно."""
        return Session(shell, emit, config)

    title = f"Эмулятор оболочки | VFS: {shell.vfs_name}"
    EmulatorWindow(title, make_session).run()


def main(argv=None):
    """Запускает эмулятор в нужном режиме."""
    config = parse_args(argv)
    shell = Shell(vfs_name(config))
    if config.headless:
        run_console(Session(shell, print, config))
    else:
        run_gui(shell, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
