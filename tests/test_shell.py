"""Тесты оболочки первого этапа: заглушки, exit, ошибки."""
import unittest

from shell import Shell


class ShellStubsTest(unittest.TestCase):
    """Команды-заглушки и служебные случаи."""

    def setUp(self):
        self.shell = Shell()

    def test_ls_prints_name_and_args(self):
        self.assertEqual(self.shell.execute("ls -l a"),
                         "ls: args=['-l', 'a']")

    def test_cd_prints_name_and_args(self):
        self.assertEqual(self.shell.execute("cd x y"),
                         "cd: args=['x', 'y']")

    def test_unknown_command(self):
        self.assertEqual(self.shell.execute("foo"),
                         "foo: command not found")

    def test_parse_error_is_reported(self):
        self.assertIn("parse error", self.shell.execute('ls "a'))

    def test_empty_line(self):
        self.assertEqual(self.shell.execute(""), "")

    def test_exit_stops_shell(self):
        self.assertTrue(self.shell.running)
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)


if __name__ == "__main__":
    unittest.main()
