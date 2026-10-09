"""Ядро оболочки: разбор строки и запуск команд."""
from commands import COMMANDS
from errors import ShellError
from lineparse import ParseError, parse_line


class Shell:
    """Состояние оболочки и выполнение введённых строк."""

    def __init__(self, vfs_name="vfs"):
        """Создаёт оболочку с именем VFS для заголовка окна."""
        self.vfs_name = vfs_name
        self.running = True

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
