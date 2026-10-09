# VFS-эмулятор оболочки (вариант 15)

## 1. Общее описание

Эмулятор командной строки UNIX-подобной ОС на Python 3.10+ с графическим интерфейсом (tkinter). Внешних зависимостей нет.

Текущий статус по этапам:

- [x] Этап 1. REPL
- [x] Этап 2. Конфигурация
- [x] Этап 3. VFS
- [x] Этап 4. Основные команды
- [ ] Этап 5. Дополнительные команды

### Этап 1. REPL

Окно содержит область вывода и строку ввода с приглашением. Заголовок окна содержит имя VFS. Парсер раскрывает переменные окружения реальной ОС. На этапе 1 команды `ls` и `cd` были заглушками, начиная с этапа 4 они полноценные. Команда `exit` закрывает окно.

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

Пути бывают абсолютными (`/docs`) и относительными (`docs/api`, `..`). Переменная `$HOME` раскрывается значением из реальной ОС, поэтому для путей VFS она обычно не подходит.

| Команда | Описание |
|---|---|
| `ls [-a] [-l] [путь...]` | Содержимое каталога. `-a` показывает скрытые (начинаются с точки), `-l` длинный формат: тип (`d` или `-`), размер, имя. Для нескольких путей печатаются заголовки |
| `cd [путь]` | Смена текущего каталога. Без аргумента переход в корень VFS |
| `pwd` | Печатает текущий каталог |
| `find [путь...] [-name шаблон] [-type f\|d]` | Рекурсивный поиск. Пути в выводе записываются так же, как указаны. Шаблон работает как `fnmatch` |
| `du [-a] [-h] [-s] [путь...]` | Размеры в байтах. По умолчанию строка на каждый каталог, `-a` добавляет файлы, `-s` только итог, `-h` читаемый вид (K, M, G) |
| `head [-n N] файл...` | Первые N строк файла, по умолчанию 10. Для нескольких файлов печатаются заголовки `==> имя <==` |
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
| `commands.py` | Реестр `COMMANDS`, команды `exit` и `vfs-info` |
| `cmd_read.py` | Команды `ls`, `cd`, `pwd`, `find`, `du`, `head` |
| `cmdutil.py` | `get_node` (поиск узла с понятной ошибкой), `split_flags` (разбор флагов), `join_path`, `node_text` |
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
sh scripts/stage4_all.sh      # все команды этапа 4 и ошибки
EMU_GUI=1 sh scripts/stage1.sh   # то же, но с окном
```

## 4. Примеры использования

Все примеры получены реальным запуском скриптов из `scripts/`. Скрипты по умолчанию работают без окна. С переменной `EMU_GUI=1` они открывают окно, например `EMU_GUI=1 sh scripts/stage4_all.sh`.

Интерактивный запуск с окном:

```sh
./run.sh --vfs examples/deep --prompt "{vfs}:{cwd}$ "
./run.sh --vfs examples/deep --script scripts/startup/all_commands.emu
```

Скриншоты в репозиторий не добавляются, потому что картинки считаются бинарными файлами. Работа окна показывается вживую.

### Этап 1. `scripts/stage1.sh`

Переменные окружения, кавычки, пустая строка, неизвестная команда, ошибка разбора.

```text
[debug] vfs = <не задан>
[debug] prompt = '$ '
[debug] script = <не задан>
[debug] headless = True
$ ls -l $HOME
ls: /home/user: No such file or directory
$ cd ${DEMO_VAR}
cd: world: No such file or directory
$ ls "two words" '$HOME'
ls: two words: No such file or directory

ls: $HOME: No such file or directory
$ ls $UNDEFINED_VAR
$ 
$ foo bar
foo: command not found
$ ls "unclosed
parse error: No closing quotation
$ exit
```

### Этап 2. `scripts/stage2_*.sh`

Параметр `--prompt` и отладочный вывод (`stage2_prompt.sh`):

```text
--- свой prompt
[debug] vfs = <не задан>
[debug] prompt = 'emu> '
[debug] script = <не задан>
[debug] headless = True
emu> ls
emu> exit
```

Параметр `--script`, ошибочные строки пропускаются (`stage2_script.sh`):

```text
--- стартовый скрипт с ошибочными строками
[debug] vfs = <не задан>
[debug] prompt = '{vfs}:{cwd}$ '
[debug] script = 'scripts/startup/basic.emu'
[debug] headless = True
# Стартовый скрипт этапа 2: диалог с ошибочными строками
vfs:/$ ls -l $HOME
ls: /home/user: No such file or directory
vfs:/$ cd /usr "two words"
cd: too many arguments
vfs:/$ unknown_command arg
unknown_command: command not found
vfs:/$ ls "незакрытая кавычка
parse error: No closing quotation
vfs:/$ cd ${HOME}/docs
cd: /home/user/docs: No such file or directory
vfs:/$ 
```

Exit внутри скрипта и несуществующий скрипт:

```text
--- exit в середине скрипта
[debug] vfs = <не задан>
[debug] prompt = '> '
[debug] script = 'scripts/startup/exit_midway.emu'
[debug] headless = True
# После exit остальные строки не выполняются
> ls before
ls: before: No such file or directory
> exit
--- несуществующий скрипт
[debug] vfs = <не задан>
[debug] prompt = '{vfs}:{cwd}$ '
[debug] script = 'scripts/startup/missing.emu'
[debug] headless = True
script: scripts/startup/missing.emu: No such file or directory
vfs:/$ 
```

### Этап 3. `scripts/stage3_*.sh`

Варианты VFS лежат в `examples/`: `minimal` (один файл), `several` (несколько файлов, есть `motd`), `deep` (четыре уровня, есть `motd`). Пример VFS `deep` и ошибки загрузки:

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
```

```text
--- каталога нет
exit code: 2
--- вместо каталога файл
exit code: 2
--- без --vfs работает пустая VFS
[debug] vfs = <не задан>
[debug] prompt = '{vfs}:{cwd}$ '
[debug] script = <не задан>
[debug] headless = True
vfs:/$ vfs-info
name: vfs
source: <память>
dirs: 0
files: 0
size: 0 bytes
depth: 0
vfs:/$ 
emulator: error: examples/missing: No such file or directory
emulator: error: examples/several/readme.txt: Not a directory
```

### Этап 4. `scripts/stage4_all.sh`

Стартовый скрипт `scripts/startup/all_commands.emu` вызывает все команды во всех режимах и с ошибками. Затем `head_ls.emu` на VFS `several` показывает скрытые файлы.

```text
--- all_commands.emu на VFS deep
[debug] vfs = 'examples/deep'
[debug] prompt = '{vfs}:{cwd}$ '
[debug] script = 'scripts/startup/all_commands.emu'
[debug] headless = True
VFS deep: три и более уровней вложенности.
# Стартовый скрипт: все команды и режимы (этапы 1-4), запускать на VFS deep
# --- служебная команда и текущий каталог
deep:/$ vfs-info
name: deep
source: examples/deep
dirs: 7
files: 8
size: 326 bytes
depth: 4
deep:/$ pwd
/
# --- ls: обычный, -a, -l, путь, файл, несколько путей
deep:/$ ls
docs  motd  src
deep:/$ ls -a
docs  motd  src
deep:/$ ls -l
d      146 docs
-       70 motd
d      110 src
deep:/$ ls docs src
docs:
api  guide.txt

src:
app  index.txt
deep:/$ ls docs/guide.txt
docs/guide.txt
# --- cd: относительный путь, .., абсолютный путь, без аргумента
deep:/$ cd docs/api
deep:/docs/api$ pwd
/docs/api
deep:/docs/api$ ls
v1  v2
deep:/docs/api$ cd ../..
deep:/$ cd /src/app
deep:/src/app$ ls -l
-       43 main.txt
d       46 util
deep:/src/app$ cd
# --- find: без аргументов, -name, -type, путь, оба условия
deep:/$ find docs
docs
docs/api
docs/api/v1
docs/api/v1/changelog.txt
docs/api/v1/spec.txt
docs/api/v2
docs/api/v2/spec.txt
docs/guide.txt
deep:/$ find -name "*.txt"
./docs/api/v1/changelog.txt
./docs/api/v1/spec.txt
./docs/api/v2/spec.txt
./docs/guide.txt
./src/app/main.txt
./src/app/util/helpers.txt
./src/index.txt
deep:/$ find src -type d
src
src/app
src/app/util
deep:/$ find / -type f -name "spec*"
/docs/api/v1/spec.txt
/docs/api/v2/spec.txt
# --- du: по умолчанию, -s, -h, -a, файл
deep:/$ du docs
75	docs/api/v1
30	docs/api/v2
105	docs/api
146	docs
deep:/$ du -s docs
146	docs
deep:/$ du -sh docs
146B	docs
deep:/$ du -a src
43	src/app/main.txt
46	src/app/util/helpers.txt
46	src/app/util
89	src/app
21	src/index.txt
110	src
deep:/$ du docs/guide.txt
41	docs/guide.txt
# --- head: по умолчанию, -n, несколько файлов
deep:/$ head docs/guide.txt
Руководство
Шаг 1
Шаг 2
deep:/$ head -n 1 docs/api/v1/spec.txt docs/api/v2/spec.txt
==> docs/api/v1/spec.txt <==
API v1

==> docs/api/v2/spec.txt <==
API v2
# --- ошибки
deep:/$ ls nothing
ls: nothing: No such file or directory
deep:/$ ls -z
ls: invalid option -- 'z'
deep:/$ cd docs/guide.txt
cd: docs/guide.txt: Not a directory
deep:/$ cd nothing
cd: nothing: No such file or directory
deep:/$ cd a b
cd: too many arguments
deep:/$ find nothing
find: nothing: No such file or directory
deep:/$ find -type x
find: Unknown argument to -type: x
deep:/$ du nothing
du: nothing: No such file or directory
deep:/$ head docs
head: docs: Is a directory
deep:/$ head nothing
head: nothing: No such file or directory
deep:/$ head -n x docs/guide.txt
head: invalid number of lines: 'x'
deep:/$ head
head: missing file operand
deep:/$ unknown_command arg
unknown_command: command not found
deep:/$ ls "незакрытая кавычка
parse error: No closing quotation
# после ошибок диалог продолжается
deep:/$ pwd
/
deep:/$ 
--- head_ls.emu на VFS several
[debug] vfs = 'examples/several'
[debug] prompt = '$ '
[debug] script = 'scripts/startup/head_ls.emu'
[debug] headless = True
Добро пожаловать в VFS several.
Введите vfs-info для сводки.
# Скрытые файлы, head и du на VFS several
$ ls
log.txt  motd  notes.txt  readme.txt
$ ls -a
.hidden  log.txt  motd  notes.txt  readme.txt
$ ls -l
-      465 log.txt
-       93 motd
-       51 notes.txt
-       42 readme.txt
$ head log.txt
строка журнала 01
строка журнала 02
строка журнала 03
строка журнала 04
строка журнала 05
строка журнала 06
строка журнала 07
строка журнала 08
строка журнала 09
строка журнала 10
$ head -n 3 notes.txt readme.txt
==> notes.txt <==
заметка 1
заметка 2
заметка 3

==> readme.txt <==
Это readme.
Вторая строка.
$ du -a
24	./.hidden
465	./log.txt
93	./motd
51	./notes.txt
42	./readme.txt
675	.
$ du -sh
675B	.
$ 
```
