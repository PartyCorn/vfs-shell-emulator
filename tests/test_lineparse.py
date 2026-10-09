"""Тесты разбора строки и раскрытия переменных."""
import unittest

from lineparse import ParseError, expand_env, parse_line

ENV = {"HOME": "/home/user", "NAME": "world"}


class ExpandEnvTest(unittest.TestCase):
    """Раскрытие переменных окружения."""

    def test_simple_variable(self):
        self.assertEqual(expand_env("$HOME/x", ENV), "/home/user/x")

    def test_braces(self):
        self.assertEqual(expand_env("${NAME}s", ENV), "worlds")

    def test_unknown_is_empty(self):
        self.assertEqual(expand_env("a$NOPE b", ENV), "a b")

    def test_single_quotes_keep_text(self):
        self.assertEqual(expand_env("'$HOME' $NAME", ENV), "'$HOME' world")

    def test_lone_dollar(self):
        self.assertEqual(expand_env("cost $ 5", ENV), "cost $ 5")


class ParseLineTest(unittest.TestCase):
    """Разбиение на токены."""

    def test_split_and_expand(self):
        self.assertEqual(parse_line("ls -l $HOME", ENV),
                         ["ls", "-l", "/home/user"])

    def test_quotes(self):
        self.assertEqual(parse_line('cd "a b" \'$HOME\'', ENV),
                         ["cd", "a b", "$HOME"])

    def test_empty_line(self):
        self.assertEqual(parse_line("   ", ENV), [])

    def test_unclosed_quote(self):
        with self.assertRaises(ParseError):
            parse_line('ls "oops', ENV)


if __name__ == "__main__":
    unittest.main()
