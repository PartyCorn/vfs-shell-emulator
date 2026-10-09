"""Тесты виртуальной файловой системы."""
import os
import tempfile
import unittest

from errors import VfsError
from vfs import VNode, Vfs, split_path

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def sample_vfs():
    """VFS: файл a.txt (3 байта) и каталог d с файлом b.txt (2 байта)."""
    root = VNode("", children={
        "a.txt": VNode("a.txt", data=b"abc"),
        "d": VNode("d", children={"b.txt": VNode("b.txt", data=b"xy")}),
    })
    return Vfs(root, "sample")


class SplitPathTest(unittest.TestCase):
    """Нормализация путей."""

    def test_relative(self):
        self.assertEqual(split_path(["a"], "b/c"), ["a", "b", "c"])

    def test_absolute(self):
        self.assertEqual(split_path(["a"], "/b"), ["b"])

    def test_dots(self):
        self.assertEqual(split_path(["a", "b"], "../c/./d"),
                         ["a", "c", "d"])

    def test_parent_of_root_is_root(self):
        self.assertEqual(split_path([], "../.."), [])


class VfsTest(unittest.TestCase):
    """Узлы, поиск, размеры, слияние."""

    def test_get_and_errors(self):
        vfs = sample_vfs()
        self.assertEqual(vfs.get(["d", "b.txt"]).data, b"xy")
        with self.assertRaises(VfsError):
            vfs.get(["nope"])
        with self.assertRaises(VfsError):
            vfs.get(["a.txt", "x"])

    def test_sizes(self):
        vfs = sample_vfs()
        self.assertEqual(vfs.root.size, 5)
        self.assertEqual(vfs.get(["d"]).size, 2)

    def test_stats(self):
        self.assertEqual(sample_vfs().stats(),
                         {"dirs": 1, "files": 2, "size": 5, "depth": 2})

    def test_clone_is_deep(self):
        vfs = sample_vfs()
        copy = vfs.get(["d"]).clone("e")
        copy.children["b.txt"].data = b"changed"
        self.assertEqual(vfs.get(["d", "b.txt"]).data, b"xy")

    def test_put_merges_directories(self):
        vfs = sample_vfs()
        extra = VNode("d", children={"c.txt": VNode("c.txt", data=b"1")})
        vfs.put(["d"], extra)
        self.assertEqual(sorted(vfs.get(["d"]).children),
                         ["b.txt", "c.txt"])

    def test_put_type_conflict(self):
        vfs = sample_vfs()
        with self.assertRaises(VfsError):
            vfs.put(["d"], VNode("d", data=b""))
        with self.assertRaises(VfsError):
            vfs.put(["a.txt"], VNode("a.txt", children={}))

    def test_put_without_parent(self):
        with self.assertRaises(VfsError):
            sample_vfs().put(["no", "f"], VNode("f"))


class LoadTest(unittest.TestCase):
    """Загрузка из каталога на диске."""

    def test_from_directory_deep(self):
        vfs = Vfs.from_directory(os.path.join(EXAMPLES, "deep"))
        self.assertEqual(vfs.name, "deep")
        self.assertIn("три", vfs.motd())
        self.assertTrue(vfs.get(["docs", "api", "v1", "spec.txt"]))
        self.assertEqual(vfs.stats()["depth"], 4)

    def test_minimal_has_no_motd(self):
        vfs = Vfs.from_directory(os.path.join(EXAMPLES, "minimal"))
        self.assertIsNone(vfs.motd())
        self.assertEqual(vfs.stats()["files"], 1)

    def test_missing_directory(self):
        with self.assertRaises(VfsError):
            Vfs.from_directory("/no/such/dir")

    def test_file_instead_of_directory(self):
        with tempfile.NamedTemporaryFile() as handle:
            with self.assertRaises(VfsError):
                Vfs.from_directory(handle.name)

    def test_memory_is_independent_of_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "f"), "wb") as handle:
                handle.write(b"data")
            vfs = Vfs.from_directory(tmp)
        self.assertEqual(vfs.get(["f"]).data, b"data")


if __name__ == "__main__":
    unittest.main()
