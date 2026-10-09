"""Виртуальная файловая система, целиком хранится в памяти."""
import os

from errors import VfsError

MOTD_NAME = "motd"


class VNode:
    """Узел VFS: файл (data) или каталог (children)."""

    def __init__(self, name, children=None, data=b""):
        """Каталог создаётся с children (dict), файл с data (bytes)."""
        self.name = name
        self.children = children
        self.data = data

    @property
    def is_dir(self):
        """Истина, если узел каталог."""
        return self.children is not None

    @property
    def size(self):
        """Размер файла или суммарный размер каталога в байтах."""
        if not self.is_dir:
            return len(self.data)
        return sum(child.size for child in self.children.values())

    def clone(self, name):
        """Глубокая копия узла под новым именем."""
        if self.is_dir:
            kids = {k: c.clone(k) for k, c in self.children.items()}
            return VNode(name, children=kids)
        return VNode(name, data=self.data)


def split_path(cwd, path):
    """Нормализует путь относительно cwd и возвращает список имён."""
    parts = [] if path.startswith("/") else list(cwd)
    for item in path.split("/"):
        if item in ("", "."):
            continue
        if item == "..":
            if parts:
                parts.pop()
        else:
            parts.append(item)
    return parts


def _read_dir(path, name):
    """Рекурсивно читает каталог диска в узлы VFS (симлинки пропускает)."""
    children = {}
    with os.scandir(path) as entries:
        for entry in sorted(entries, key=lambda e: e.name):
            if entry.is_symlink():
                continue
            if entry.is_dir():
                children[entry.name] = _read_dir(entry.path, entry.name)
            else:
                with open(entry.path, "rb") as handle:
                    children[entry.name] = VNode(entry.name,
                                                 data=handle.read())
    return VNode(name, children=children)


def _merge(existing, node):
    """Сливает каталог node в каталог existing, файлы заменяет."""
    for name, child in node.children.items():
        old = existing.children.get(name)
        if old is not None and old.is_dir and child.is_dir:
            _merge(old, child)
        else:
            existing.children[name] = child.clone(name)


def _count(node, level):
    """Возвращает (каталогов, файлов, глубина) поддерева узла."""
    if not node.is_dir:
        return 0, 1, level
    dirs, files, depth = 1, 0, level
    for child in node.children.values():
        sub_dirs, sub_files, sub_depth = _count(child, level + 1)
        dirs += sub_dirs
        files += sub_files
        depth = max(depth, sub_depth)
    return dirs, files, depth


class Vfs:
    """Дерево узлов в памяти, источником служит каталог на диске."""

    def __init__(self, root=None, name="vfs", source=None):
        """Без аргументов создаёт пустую VFS."""
        self.root = root if root is not None else VNode("", children={})
        self.name = name
        self.source = source

    @classmethod
    def from_directory(cls, path):
        """Читает каталог диска в память. Диск после этого не нужен."""
        real = os.path.abspath(path)
        if not os.path.exists(real):
            raise VfsError(f"{path}: No such file or directory")
        if not os.path.isdir(real):
            raise VfsError(f"{path}: Not a directory")
        try:
            root = _read_dir(real, "")
        except OSError as err:
            raise VfsError(f"{path}: {err.strerror}") from err
        return cls(root, os.path.basename(real) or "root", path)

    def get(self, parts):
        """Возвращает узел по списку имён или поднимает VfsError."""
        node = self.root
        for part in parts:
            if not node.is_dir:
                raise VfsError("Not a directory")
            node = node.children.get(part)
            if node is None:
                raise VfsError("No such file or directory")
        return node

    def find(self, parts):
        """Как get, но возвращает None, если узла нет."""
        try:
            return self.get(parts)
        except VfsError:
            return None

    def put(self, parts, node):
        """Кладёт узел по пути. Каталоги сливаются, файлы заменяются."""
        parent = self.get(parts[:-1])
        if not parent.is_dir:
            raise VfsError("Not a directory")
        name = parts[-1]
        old = parent.children.get(name)
        if old is not None and old.is_dir and node.is_dir:
            _merge(old, node)
        elif old is not None and old.is_dir:
            raise VfsError("cannot overwrite directory with non-directory")
        elif old is not None and node.is_dir:
            raise VfsError("cannot overwrite non-directory with directory")
        else:
            parent.children[name] = node.clone(name)

    def motd(self):
        """Текст motd из корня VFS или None, если файла нет."""
        node = self.root.children.get(MOTD_NAME)
        if node is None or node.is_dir:
            return None
        return node.data.decode("utf-8", errors="replace").rstrip("\n")

    def stats(self):
        """Сводка: каталоги, файлы, размер, максимальная глубина."""
        dirs, files, depth = _count(self.root, 0)
        return {"dirs": dirs - 1, "files": files,
                "size": self.root.size, "depth": depth}
