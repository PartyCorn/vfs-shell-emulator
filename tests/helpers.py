"""Общие помощники тестов: VFS из словаря."""
from shell import Shell
from vfs import VNode, Vfs

TREE = {
    "a.txt": "one\ntwo\nthree\n",
    ".hid": "x",
    "docs": {
        "guide.txt": "guide",
        "api": {"v1": {"spec.txt": "spec"}},
    },
    "empty": {},
}


def node_from(name, value):
    """Строит узел: dict даёт каталог, строка даёт файл."""
    if isinstance(value, dict):
        kids = {k: node_from(k, v) for k, v in value.items()}
        return VNode(name, children=kids)
    return VNode(name, data=value.encode("utf-8"))


def make_shell(tree=None):
    """Оболочка над VFS, собранной из словаря (по умолчанию TREE)."""
    root = node_from("", TREE if tree is None else tree)
    return Shell(Vfs(root, "test"))
