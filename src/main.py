"""Точка входа эмулятора."""
import sys

from config import parse_args
from errors import VfsError
from session import Session
from shell import Shell
from vfs import Vfs

EXIT_BAD_VFS = 2


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


def load_vfs(config):
    """Загружает VFS из каталога --vfs или создаёт пустую."""
    if config.vfs:
        return Vfs.from_directory(config.vfs)
    return Vfs()


def run_gui(shell, config):
    """Запускает графический интерфейс."""
    from gui import EmulatorWindow

    def make_session(emit):
        """Создаёт сессию с выводом в окно."""
        return Session(shell, emit, config)

    title = f"Эмулятор оболочки | VFS: {shell.vfs.name}"
    EmulatorWindow(title, make_session).run()


def main(argv=None):
    """Запускает эмулятор в нужном режиме."""
    config = parse_args(argv)
    try:
        shell = Shell(load_vfs(config))
    except VfsError as err:
        print(f"emulator: error: {err}", file=sys.stderr)
        return EXIT_BAD_VFS
    if config.headless:
        run_console(Session(shell, print, config))
    else:
        run_gui(shell, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
