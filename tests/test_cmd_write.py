"""Тесты команд touch и cp."""
import os
import unittest

from helpers import make_shell
from vfs import Vfs

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


class TouchTest(unittest.TestCase):
    """Команда touch."""

    def setUp(self):
        self.sh = make_shell()

    def test_creates_empty_file(self):
        self.assertEqual(self.sh.execute("touch new.txt"), "")
        node = self.sh.vfs.get(["new.txt"])
        self.assertFalse(node.is_dir)
        self.assertEqual(node.size, 0)

    def test_visible_in_ls(self):
        self.sh.execute("touch new.txt")
        self.assertIn("new.txt", self.sh.execute("ls"))

    def test_existing_file_keeps_data(self):
        self.sh.execute("touch a.txt")
        self.assertEqual(self.sh.vfs.get(["a.txt"]).size, 14)

    def test_several_files_and_cwd(self):
        self.sh.execute("cd docs")
        self.sh.execute("touch x y ../z")
        self.assertEqual(self.sh.execute("ls -a /").count("z"), 1)
        self.assertIn("x", self.sh.vfs.get(["docs"]).children)

    def test_missing_parent(self):
        self.assertEqual(self.sh.execute("touch nodir/x"),
                         "touch: nodir/x: No such file or directory")

    def test_parent_is_file(self):
        self.assertIn("Not a directory", self.sh.execute("touch a.txt/x"))

    def test_error_does_not_stop_others(self):
        out = self.sh.execute("touch nodir/x ok.txt")
        self.assertIn("No such file", out)
        self.assertIsNotNone(self.sh.vfs.find(["ok.txt"]))

    def test_errors(self):
        self.assertIn("missing file", self.sh.execute("touch"))
        self.assertIn("invalid option", self.sh.execute("touch -z x"))


class CpFileTest(unittest.TestCase):
    """Копирование файлов."""

    def setUp(self):
        self.sh = make_shell()

    def test_new_name(self):
        self.assertEqual(self.sh.execute("cp a.txt b.txt"), "")
        self.assertEqual(self.sh.vfs.get(["b.txt"]).data,
                         self.sh.vfs.get(["a.txt"]).data)

    def test_copy_is_independent(self):
        self.sh.execute("cp a.txt b.txt")
        self.sh.vfs.get(["b.txt"]).data = b"changed"
        self.assertEqual(self.sh.vfs.get(["a.txt"]).size, 14)

    def test_overwrite(self):
        self.sh.execute("cp docs/guide.txt a.txt")
        self.assertEqual(self.sh.vfs.get(["a.txt"]).data, b"guide")

    def test_into_directory(self):
        self.sh.execute("cp a.txt empty")
        self.assertIn("a.txt", self.sh.vfs.get(["empty"]).children)

    def test_many_into_directory(self):
        self.sh.execute("cp a.txt docs/guide.txt empty/")
        self.assertEqual(sorted(self.sh.vfs.get(["empty"]).children),
                         ["a.txt", "guide.txt"])

    def test_relative_after_cd(self):
        self.sh.execute("cd docs")
        self.sh.execute("cp guide.txt ../g2.txt")
        self.assertIsNotNone(self.sh.vfs.find(["g2.txt"]))


class CpDirTest(unittest.TestCase):
    """Копирование каталогов и ошибки."""

    def setUp(self):
        self.sh = make_shell()

    def test_without_r(self):
        self.assertIn("-r not specified", self.sh.execute("cp docs d2"))
        self.assertIsNone(self.sh.vfs.find(["d2"]))

    def test_recursive_new_name(self):
        self.sh.execute("cp -r docs d2")
        self.assertEqual(self.sh.vfs.get(["d2", "api", "v1", "spec.txt"])
                         .data, b"spec")

    def test_recursive_uppercase_flag(self):
        self.sh.execute("cp -R docs d2")
        self.assertIsNotNone(self.sh.vfs.find(["d2"]))

    def test_recursive_into_existing_directory(self):
        self.sh.execute("cp -r docs empty")
        self.assertIsNotNone(self.sh.vfs.find(["empty", "docs", "api"]))

    def test_merge_keeps_old_files(self):
        self.sh.execute("cp -r docs/api empty")
        self.sh.execute("touch empty/api/extra")
        self.sh.execute("cp -r docs/api empty")
        self.assertIsNotNone(self.sh.vfs.find(["empty", "api", "extra"]))
        self.assertIsNotNone(self.sh.vfs.find(["empty", "api", "v1"]))

    def test_errors(self):
        run = self.sh.execute
        self.assertIn("missing file operand", run("cp"))
        self.assertIn("missing destination", run("cp a.txt"))
        self.assertIn("No such file", run("cp nothing x"))
        self.assertIn("No such file", run("cp a.txt nodir/x"))
        self.assertIn("not a directory", run("cp a.txt docs/guide.txt x"))
        self.assertIn("same file", run("cp a.txt a.txt"))
        self.assertIn("same file", run("cp a.txt ."))
        self.assertIn("into itself", run("cp -r docs docs/api"))
        self.assertIn("into itself", run("cp -r / docs"))
        self.assertIn("cannot overwrite", run("cp -r docs a.txt"))
        run("cp a.txt api")
        self.assertIn("cannot overwrite", run("cp api docs"))
        self.assertIn("Not a directory", run("cp a.txt a.txt/x"))

    def test_error_does_not_stop_other_sources(self):
        self.sh.execute("cp nothing a.txt empty")
        self.assertIn("a.txt", self.sh.vfs.get(["empty"]).children)


class DiskUntouchedTest(unittest.TestCase):
    """Изменения VFS не затрагивают каталог на диске."""

    def test_disk_listing_is_same(self):
        path = os.path.join(EXAMPLES, "deep")
        before = sorted(os.walk(path))
        shell = make_shell()
        shell.vfs = Vfs.from_directory(path)
        shell.execute("touch new.txt")
        shell.execute("cp -r docs docs2")
        self.assertEqual(sorted(os.walk(path)), before)
        self.assertIsNotNone(shell.vfs.find(["docs2", "guide.txt"]))


if __name__ == "__main__":
    unittest.main()
