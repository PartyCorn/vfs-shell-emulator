"""Точка входа эмулятора."""
import sys

from config import parse_args
from session import Session
from shell import Shell


def run_console(session):
    """Консольный цикл: читает строки со стандартного ввода."""
    while session.shell.running:
        try:
            line = input(session.prompt_text())
        except EOFError:
            break
        if not sys.stdin.isatty():
            print(line)
        session.submit(line, echo=False)


def run_gui(shell):
    """Запускает графический интерфейс."""
    from gui import EmulatorWindow

    def make_session(emit):
        """Создаёт сессию с выводом в окно."""
        return Session(shell, emit)

    title = f"Эмулятор оболочки | VFS: {shell.vfs_name}"
    EmulatorWindow(title, make_session).run()


def main(argv=None):
    """Запускает эмулятор в нужном режиме."""
    config = parse_args(argv)
    shell = Shell()
    if config.headless:
        run_console(Session(shell, print))
    else:
        run_gui(shell)
    return 0


if __name__ == "__main__":
    sys.exit(main())
