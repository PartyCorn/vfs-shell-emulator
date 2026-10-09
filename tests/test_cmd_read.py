"""Тесты команд ls, cd, pwd, find, du, head."""
import unittest

from helpers import make_shell


class LsTest(unittest.TestCase):
    """Команда ls."""

    def setUp(self):
        self.sh = make_shell()

    def test_plain_hides_hidden(self):
        self.assertEqual(self.sh.execute("ls"), "a.txt  docs  empty")

    def test_all_shows_hidden(self):
        self.assertEqual(self.sh.execute("ls -a"),
                         ".hid  a.txt  docs  empty")

    def test_long_format(self):
        out = self.sh.execute("ls -l docs")
        self.assertEqual(out.splitlines(),
                         ["d        4 api", "-        5 guide.txt"])

    def test_file_argument(self):
        self.assertEqual(self.sh.execute("ls a.txt"), "a.txt")

    def test_several_paths_have_titles(self):
        out = self.sh.execute("ls docs empty")
        self.assertEqual(out, "docs:\napi  guide.txt\n\nempty:\n")

    def test_missing_path(self):
        self.assertEqual(self.sh.execute("ls nope"),
                         "ls: nope: No such file or directory")

    def test_bad_option(self):
        self.assertIn("invalid option", self.sh.execute("ls -z"))

    def test_error_does_not_stop_other_paths(self):
        out = self.sh.execute("ls nope docs")
        self.assertIn("No such file", out)
        self.assertIn("guide.txt", out)


class CdPwdTest(unittest.TestCase):
    """Команды cd и pwd."""

    def setUp(self):
        self.sh = make_shell()

    def test_cd_and_pwd(self):
        self.sh.execute("cd docs/api")
        self.assertEqual(self.sh.execute("pwd"), "/docs/api")

    def test_cd_changes_ls(self):
        self.sh.execute("cd docs")
        self.assertEqual(self.sh.execute("ls"), "api  guide.txt")

    def test_cd_parent_and_root(self):
        self.sh.execute("cd docs/api/v1")
        self.sh.execute("cd ../..")
        self.assertEqual(self.sh.execute("pwd"), "/docs")
        self.sh.execute("cd")
        self.assertEqual(self.sh.execute("pwd"), "/")

    def test_cd_absolute(self):
        self.sh.execute("cd docs")
        self.sh.execute("cd /empty")
        self.assertEqual(self.sh.execute("pwd"), "/empty")

    def test_cd_to_file(self):
        self.assertEqual(self.sh.execute("cd a.txt"),
                         "cd: a.txt: Not a directory")

    def test_cd_missing_keeps_cwd(self):
        self.sh.execute("cd docs")
        self.assertIn("No such file", self.sh.execute("cd nope"))
        self.assertEqual(self.sh.execute("pwd"), "/docs")

    def test_cd_too_many_arguments(self):
        self.assertIn("too many", self.sh.execute("cd a b"))


class FindTest(unittest.TestCase):
    """Команда find."""

    def setUp(self):
        self.sh = make_shell()

    def test_all(self):
        out = self.sh.execute("find").splitlines()
        self.assertEqual(out[0], ".")
        self.assertIn("./docs/api/v1/spec.txt", out)
        self.assertIn("./.hid", out)

    def test_path(self):
        out = self.sh.execute("find docs/api").splitlines()
        self.assertEqual(out, ["docs/api", "docs/api/v1",
                               "docs/api/v1/spec.txt"])

    def test_name(self):
        out = self.sh.execute("find -name '*.txt'").splitlines()
        self.assertEqual(out, ["./a.txt", "./docs/api/v1/spec.txt",
                               "./docs/guide.txt"])

    def test_type_d(self):
        out = self.sh.execute("find / -type d").splitlines()
        self.assertEqual(out, ["/", "/docs", "/docs/api", "/docs/api/v1",
                               "/empty"])

    def test_name_and_type(self):
        self.assertEqual(self.sh.execute("find docs -type d -name v1"),
                         "docs/api/v1")

    def test_errors(self):
        self.assertIn("No such file", self.sh.execute("find nope"))
        self.assertIn("unknown predicate", self.sh.execute("find -size"))
        self.assertIn("Unknown argument", self.sh.execute("find -type x"))
        self.assertIn("missing argument", self.sh.execute("find -name"))


class DuTest(unittest.TestCase):
    """Команда du."""

    def setUp(self):
        self.sh = make_shell()

    def test_default_lists_directories(self):
        out = self.sh.execute("du docs").splitlines()
        self.assertEqual(out, ["4\tdocs/api/v1", "4\tdocs/api",
                               "9\tdocs"])

    def test_summary(self):
        self.assertEqual(self.sh.execute("du -s docs"), "9\tdocs")

    def test_all_files(self):
        out = self.sh.execute("du -a docs").splitlines()
        self.assertIn("5\tdocs/guide.txt", out)

    def test_file(self):
        self.assertEqual(self.sh.execute("du a.txt"), "14\ta.txt")

    def test_human(self):
        self.assertEqual(self.sh.execute("du -sh a.txt"), "14B\ta.txt")

    def test_human_units(self):
        from cmd_read import human_size
        self.assertEqual(human_size(1536), "1.5K")
        self.assertEqual(human_size(3 * 1024 * 1024), "3.0M")

    def test_missing(self):
        self.assertIn("No such file", self.sh.execute("du nope"))


class HeadTest(unittest.TestCase):
    """Команда head."""

    def setUp(self):
        text = "".join(f"line {i}\n" for i in range(1, 16))
        self.sh = make_shell({"f": text, "g": "g1\ng2\n", "d": {}})

    def test_default_ten_lines(self):
        out = self.sh.execute("head f").splitlines()
        self.assertEqual(len(out), 10)
        self.assertEqual(out[-1], "line 10")

    def test_n_option(self):
        self.assertEqual(self.sh.execute("head -n 2 f"), "line 1\nline 2")
        self.assertEqual(self.sh.execute("head -n1 f"), "line 1")

    def test_zero_lines(self):
        self.assertEqual(self.sh.execute("head -n 0 f"), "")

    def test_many_files_have_titles(self):
        out = self.sh.execute("head -n 1 f g")
        self.assertEqual(out, "==> f <==\nline 1\n\n==> g <==\ng1")

    def test_errors(self):
        self.assertIn("Is a directory", self.sh.execute("head d"))
        self.assertIn("No such file", self.sh.execute("head nope"))
        self.assertIn("invalid number", self.sh.execute("head -n x f"))
        self.assertIn("invalid number", self.sh.execute("head -n -3 f"))
        self.assertIn("invalid number", self.sh.execute("head -n"))
        self.assertIn("missing file", self.sh.execute("head"))
        self.assertIn("invalid option", self.sh.execute("head -x f"))


if __name__ == "__main__":
    unittest.main()
