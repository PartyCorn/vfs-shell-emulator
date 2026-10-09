"""Тесты оболочки: разбор, exit, ошибки."""
import unittest

from shell import Shell


class ShellTest(unittest.TestCase):
    """Служебные случаи оболочки."""

    def setUp(self):
        self.shell = Shell()

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

    def test_help_lists_all_commands(self):
        out = self.shell.execute("help")
        self.assertIn("cp [-r]", out)
        self.assertIn("exit", out)

    def test_help_for_one_command(self):
        self.assertTrue(self.shell.execute("help ls").startswith("ls"))

    def test_help_unknown(self):
        self.assertIn("no help", self.shell.execute("help nope"))


if __name__ == "__main__":
    unittest.main()
