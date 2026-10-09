"""Сессия диалога: приглашение, эхо ввода, стартовый скрипт."""
from config import format_debug

COMMENT_MARK = "#"


class Session:
    """Связывает оболочку с выводом (окно GUI или консоль)."""

    def __init__(self, shell, emit, config):
        """emit(text) выводит строку пользователю."""
        self.shell = shell
        self.emit = emit
        self.config = config

    def prompt_text(self):
        """Приглашение, {vfs} и {cwd} заменяются текущими значениями."""
        text = self.config.prompt.replace("{vfs}", self.shell.vfs.name)
        return text.replace("{cwd}", self.shell.cwd_text())

    def start(self):
        """Печатает параметры и motd, выполняет стартовый скрипт."""
        for line in format_debug(self.config):
            self.emit(line)
        motd = self.shell.vfs.motd()
        if motd is not None:
            self.emit(motd)
        if self.config.script:
            self.run_script(self.config.script)

    def submit(self, line, echo=True):
        """Выполняет строку; echo показывает приглашение и ввод."""
        if echo:
            self.emit(self.prompt_text() + line)
        output = self.shell.execute(line)
        if output:
            self.emit(output)

    def run_script(self, path):
        """Строка за строкой выполняет скрипт, как будто его вводят."""
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except (OSError, UnicodeDecodeError) as err:
            reason = getattr(err, "strerror", None) or str(err)
            self.emit(f"script: {path}: {reason}")
            return
        for line in lines:
            if not self.shell.running:
                break
            self.play_line(line)

    def play_line(self, line):
        """Пустые строки пропускает, комментарии печатает, остальное
        выполняет. Ошибочная строка даёт сообщение, скрипт идёт дальше."""
        text = line.strip()
        if not text:
            return
        if text.startswith(COMMENT_MARK):
            self.emit(text)
            return
        self.submit(line)
