# VFS-эмулятор оболочки (вариант 15)

## 1. Общее описание

Эмулятор командной строки UNIX-подобной ОС на Python 3.10+ с графическим интерфейсом (tkinter). Внешних зависимостей нет.

Текущий статус по этапам:

- [x] Этап 1. REPL
- [x] Этап 2. Конфигурация
- [x] Этап 3. VFS
- [ ] Этап 4. Основные команды
- [ ] Этап 5. Дополнительные команды

### Этап 1. REPL

Окно содержит область вывода и строку ввода с приглашением. Заголовок окна содержит имя VFS. Парсер раскрывает переменные окружения реальной ОС. Команды `ls` и `cd` пока заглушки. Команда `exit` закрывает окно.

## 2. Описание всех функций и настроек

### Параметры командной строки

| Параметр | Описание |
|---|---|
| `--vfs PATH` | Каталог на диске, из которого строится VFS |
| `--prompt STR` | Приглашение. Можно использовать `{vfs}` (имя VFS) и `{cwd}` (текущий каталог). По умолчанию `{vfs}:{cwd}$ ` |
| `--script PATH` | Стартовый скрипт эмулятора |
| `--headless` | Консольный режим без окна. Нужен для тестов и скриптов |

При запуске эмулятор выводит отладочные строки `[debug] имя = значение` для всех параметров.

### Команды

| Команда | Описание |
|---|---|
| `ls [args]` | Заглушка, печатает имя и аргументы |
| `cd [args]` | Заглушка, печатает имя и аргументы |
| `exit` | Завершает работу эмулятора |
| `vfs-info` | Служебная команда: имя, источник, число каталогов и файлов, размер, глубина VFS |

### VFS

- Источник VFS: каталог на диске, который указан в `--vfs`. Без параметра работает пустая VFS с именем `vfs`.
- Каталог читается в память целиком при старте. Все операции идут над деревом в памяти, диск не изменяется.
- Имя VFS равно имени каталога. Оно показывается в заголовке окна и в приглашении.
- Если в корне VFS есть файл `motd`, его текст выводится при старте после отладочных строк.
- Символические ссылки при загрузке пропускаются.
- Если каталог не найден или это файл, эмулятор печатает ошибку в stderr и завершается с кодом 2.

### Стартовый скрипт

Файл с командами эмулятора, одна команда на строку.

- Строки выполняются по очереди, на экране видны приглашение, ввод и вывод.
- Пустые строки пропускаются, строки с `#` выводятся как комментарий.
- Ошибочная строка даёт сообщение об ошибке, выполнение идёт дальше.
- `exit` останавливает скрипт и закрывает эмулятор.
- Если файл не найден, печатается ошибка и эмулятор работает в обычном режиме.

### Синтаксис строки

- `$VAR` и `${VAR}` заменяются значением переменной окружения. Неизвестная переменная даёт пустую строку.
- Одинарные кавычки отключают раскрытие, двойные нет.
- Аргументы разделяются пробелами, кавычки группируют слова.
- Незакрытая кавычка даёт ошибку `parse error`.
- Неизвестная команда даёт `<имя>: command not found`.

### Модули (`src/`)

| Модуль | Назначение |
|---|---|
| `main.py` | Точка входа. `main`, `run_gui`, `run_console` |
| `config.py` | Разбор параметров. `parse_args`, `build_parser`, `format_debug` |
| `lineparse.py` | `expand_env` раскрывает переменные, `parse_line` делит строку на токены |
| `shell.py` | Класс `Shell`. `execute` выполняет строку, `resolve` строит путь от корня, `cwd_text` печатает текущий каталог |
| `commands.py` | Реестр `COMMANDS` и сами команды |
| `session.py` | Класс `Session`. Приглашение, эхо ввода, отладочный вывод, `run_script` и `play_line` для скриптов |
| `gui.py` | Класс `EmulatorWindow`. Окно, ввод, история команд (стрелки вверх и вниз) |
| `vfs.py` | Класс `Vfs` (`from_directory`, `get`, `find`, `put`, `motd`, `stats`), узел `VNode` (`size`, `clone`), функция `split_path` |
| `errors.py` | Исключения `ShellError` и `VfsError` |

## 3. Команды сборки и запуска тестов

Сборка не нужна. Нужны Python 3.10+ и tkinter (на Debian и Ubuntu пакет `python3-tk`).

```sh
make run          # запуск с окном (или ./run.sh)
make test         # модульные тесты (unittest)
make demo         # все демонстрационные скрипты
sh scripts/stage1.sh   # демо этапа 1 без окна
sh scripts/stage2_prompt.sh   # параметр --prompt
sh scripts/stage2_script.sh   # параметр --script
sh scripts/stage2_all.sh      # все параметры и ошибки параметров
sh scripts/stage3_vfs.sh      # разные VFS и motd
sh scripts/stage3_errors.sh   # ошибки загрузки VFS
sh scripts/stage3_all.sh      # общий стартовый скрипт на разных VFS
EMU_GUI=1 sh scripts/stage1.sh   # то же, но с окном
```

## 4. Примеры использования

### Этап 1. Скрипт `scripts/stage1.sh`

Скрипт показывает раскрытие переменных, кавычки, пустую строку и ошибки. Вывод получен реальным запуском.

```text
$ ls -l $HOME
ls: args=['-l', '/home/user']
$ cd ${DEMO_VAR} "two words" '$HOME'
cd: args=['world', 'two words', '$HOME']
$ ls $UNDEFINED_VAR end
ls: args=['end']
$ 
$ foo bar
foo: command not found
$ ls "unclosed
parse error: No closing quotation
$ exit
```

### Этап 2. Скрипты `scripts/stage2_*.sh`

Скрипты реальной ОС вызывают эмулятор со всеми параметрами. Стартовые скрипты эмулятора лежат в `scripts/startup/`.

Параметр `--prompt` (фрагмент вывода `stage2_prompt.sh`):

```text
--- без параметров
[debug] vfs = <не задан>
[debug] prompt = '$ '
[debug] script = <не задан>
[debug] headless = True
$ ls
ls: args=[]
$ exit
--- свой prompt
[debug] vfs = <не задан>
[debug] prompt = 'emu> '
[debug] script = <не задан>
```

Параметр `--script` (фрагмент вывода `stage2_script.sh`):

```text
--- стартовый скрипт с ошибочными строками
[debug] vfs = <не задан>
[debug] prompt = '$ '
[debug] script = 'scripts/startup/basic.emu'
[debug] headless = True
# Стартовый скрипт этапа 2: диалог с ошибочными строками
$ ls -l $HOME
ls: args=['-l', '/home/user']
$ cd /usr "two words"
cd: args=['/usr', 'two words']
$ unknown_command arg
unknown_command: command not found
$ ls "незакрытая кавычка
parse error: No closing quotation
$ cd ${HOME}/docs
cd: args=['/home/user/docs']
$ 
--- exit в середине скрипта
[debug] vfs = <не задан>
[debug] prompt = '> '
[debug] script = 'scripts/startup/exit_midway.emu'
[debug] headless = True
```

### Этап 3. Скрипты `scripts/stage3_*.sh`

Три варианта VFS лежат в `examples/`: `minimal` (один файл), `several` (несколько файлов, есть `motd`), `deep` (четыре уровня вложенности, есть `motd`). Общий стартовый скрипт `scripts/startup/all_commands.emu` вызывает все команды с ошибками, он запускается на разных VFS в `stage3_all.sh`.

VFS `deep` с motd и служебной командой:

```text
--- VFS deep
[debug] vfs = 'examples/deep'
[debug] prompt = '{vfs}:{cwd}$ '
[debug] script = <не задан>
[debug] headless = True
VFS deep: три и более уровней вложенности.
deep:/$ vfs-info
name: deep
source: examples/deep
dirs: 7
files: 8
size: 326 bytes
depth: 4
deep:/$ 
--- имя VFS в приглашении
VFS deep: три и более уровней вложенности.
[deep] /> vfs-info
name: deep
source: examples/deep
dirs: 7
files: 8
size: 326 bytes
depth: 4
```

Ошибки загрузки:

```text
--- каталога нет
emulator: error: examples/missing: No such file or directory
exit code: 2
--- вместо каталога файл
emulator: error: examples/several/readme.txt: Not a directory
exit code: 2
```
