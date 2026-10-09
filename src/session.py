"""Сессия диалога: приглашение, эхо ввода и вывод результатов."""


class Session:
    """Связывает оболочку с выводом (окно GUI или консоль)."""

    def __init__(self, shell, emit, prompt="$ "):
        """emit(text) выводит строку пользователю."""
        self.shell = shell
        self.emit = emit
        self.prompt = prompt

    def prompt_text(self):
        """Текущее приглашение к вводу."""
        return self.prompt

    def submit(self, line, echo=True):
        """Выполняет строку; echo показывает приглашение и ввод."""
        if echo:
            self.emit(self.prompt_text() + line)
        output = self.shell.execute(line)
        if output:
            self.emit(output)
