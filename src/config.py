"""Параметры командной строки и их отладочный вывод."""
import argparse

NOT_SET = "<не задан>"
DEFAULT_PROMPT = "{vfs}:{cwd}$ "


def build_parser():
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки UNIX-подобной ОС с GUI"
    )
    parser.add_argument(
        "--vfs", metavar="PATH",
        help="каталог на диске, источник VFS",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT,
        help="приглашение, можно {vfs} и {cwd}",
    )
    parser.add_argument(
        "--script", metavar="PATH",
        help="путь к стартовому скрипту эмулятора",
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="консольный режим без окна (для тестов и CI)",
    )
    return parser


def parse_args(argv=None):
    """Разбирает аргументы, argv=None означает sys.argv."""
    return build_parser().parse_args(argv)


def format_debug(config):
    """Возвращает строки отладочного вывода всех параметров."""
    lines = []
    for name, value in vars(config).items():
        shown = NOT_SET if value is None else repr(value)
        lines.append(f"[debug] {name} = {shown}")
    return lines
