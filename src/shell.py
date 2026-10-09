"""Ядро оболочки: разбор строки и запуск команд."""
from commands import COMMANDS
from errors import ShellError
from lineparse import ParseError, parse_line
from vfs import Vfs, split_path


class Shell:
    """Состояние оболочки и выполнение введённых строк."""

    def __init__(self, vfs=None):
        """Создаёт оболочку над VFS, по умолчанию пустой."""
        self.vfs = vfs if vfs is not None else Vfs()
        self.cwd = []
        self.running = True

    def resolve(self, path):
        """Превращает путь пользователя в список имён от корня."""
        return split_path(self.cwd, path)

    def cwd_text(self):
        """Текущий каталог в виде строки, например /docs/api."""
        return "/" + "/".join(self.cwd)

    def execute(self, line):
        """Выполняет строку и возвращает текст вывода или ошибки."""
        try:
            tokens = parse_line(line)
        except ParseError as err:
            return f"parse error: {err}"
        if not tokens:
            return ""
        handler = COMMANDS.get(tokens[0])
        if handler is None:
            return f"{tokens[0]}: command not found"
        try:
            return handler(self, tokens[1:])
        except ShellError as err:
            return str(err)
