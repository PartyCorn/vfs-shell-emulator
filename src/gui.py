"""Графический интерфейс на tkinter."""
import tkinter as tk

BG_COLOR = "#1e1e1e"
FG_COLOR = "#d4d4d4"
FONT = ("DejaVu Sans Mono", 15)
WINDOW_SIZE = "1100x700"
START_DELAY_MS = 100


class EmulatorWindow:
    """Окно: область вывода сверху, строка ввода снизу."""

    def __init__(self, title, make_session):
        """make_session(emit) создаёт сессию, привязанную к окну."""
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(WINDOW_SIZE)
        self.history = []
        self.history_pos = 0
        self._build_widgets()
        self.session = make_session(self.write)
        self.refresh_prompt()
        self.entry.focus_set()
        self.root.after(START_DELAY_MS, self.start)

    def start(self):
        """Запускает отладочный вывод и стартовый скрипт."""
        self.session.start()
        self.refresh_prompt()
        self.close_if_done()

    def _build_widgets(self):
        """Создаёт и раскладывает виджеты."""
        bottom = tk.Frame(self.root, bg=BG_COLOR)
        bottom.pack(side="bottom", fill="x")
        self.prompt_label = tk.Label(
            bottom, bg=BG_COLOR, fg=FG_COLOR, font=FONT
        )
        self.prompt_label.pack(side="left")
        self.entry = tk.Entry(
            bottom, bg=BG_COLOR, fg=FG_COLOR, font=FONT,
            insertbackground=FG_COLOR, relief="flat",
            highlightthickness=0, cursor=f"xterm {FG_COLOR}"
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.output = tk.Text(
            self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT,
            state="disabled", wrap="word",
            cursor=f"left_ptr {FG_COLOR}"
        )
        self.output.pack(side="top", fill="both", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Up>", lambda _e: self.on_history(-1))
        self.entry.bind("<Down>", lambda _e: self.on_history(1))

    def write(self, text):
        """Добавляет строку в область вывода."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.configure(state="disabled")
        self.output.see("end")

    def refresh_prompt(self):
        """Обновляет текст приглашения слева от поля ввода."""
        self.prompt_label.configure(text=self.session.prompt_text())

    def close_if_done(self):
        """Закрывает окно, если выполнена команда exit."""
        if not self.session.shell.running:
            self.root.destroy()

    def on_enter(self, _event):
        """Обрабатывает нажатие Enter."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.history.append(line)
        self.history_pos = len(self.history)
        self.session.submit(line)
        self.refresh_prompt()
        self.close_if_done()

    def on_history(self, step):
        """Листает историю команд стрелками вверх и вниз."""
        pos = self.history_pos + step
        if pos not in range(len(self.history) + 1):
            return "break"
        self.history_pos = pos
        self.entry.delete(0, "end")
        if pos < len(self.history):
            self.entry.insert(0, self.history[pos])
        return "break"

    def run(self):
        """Запускает главный цикл окна."""
        self.root.mainloop()
