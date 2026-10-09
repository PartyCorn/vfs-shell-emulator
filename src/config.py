"""Параметры командной строки."""
import argparse


def build_parser():
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки UNIX-подобной ОС с GUI"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="консольный режим без окна (для тестов и CI)",
    )
    return parser


def parse_args(argv=None):
    """Разбирает аргументы, argv=None означает sys.argv."""
    return build_parser().parse_args(argv)
