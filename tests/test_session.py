"""Тесты конфигурации, отладочного вывода и стартового скрипта."""
import os
import tempfile
import unittest

from config import format_debug, parse_args
from session import Session
from shell import Shell
from vfs import VNode


def make_session(argv=()):
    """Сессия, которая складывает вывод в список."""
    out = []
    config = parse_args(list(argv))
    return Session(Shell(), out.append, config), out


class ConfigTest(unittest.TestCase):
    """Разбор параметров и отладочный вывод."""

    def test_defaults(self):
        config = parse_args([])
        self.assertEqual(config.prompt, "{vfs}:{cwd}$ ")
        self.assertIsNone(config.vfs)
        self.assertIsNone(config.script)

    def test_all_params(self):
        config = parse_args(["--vfs", "d", "--prompt", ">", "--script", "s"])
        self.assertEqual((config.vfs, config.prompt, config.script),
                         ("d", ">", "s"))

    def test_debug_lists_every_param(self):
        lines = format_debug(parse_args(["--prompt", "> "]))
        self.assertIn("[debug] prompt = '> '", lines)
        self.assertIn("[debug] vfs = <не задан>", lines)
        self.assertEqual(len(lines), len(vars(parse_args([]))))


class SessionTest(unittest.TestCase):
    """Приглашение, эхо и скрипты."""

    def test_submit_echoes_prompt(self):
        session, out = make_session(["--prompt", "> "])
        session.submit("ls a")
        self.assertEqual(out, ["> ls a", "ls: args=['a']"])

    def test_start_prints_debug(self):
        session, out = make_session()
        session.start()
        self.assertTrue(out[0].startswith("[debug]"))

    def test_script_skips_bad_lines_and_continues(self):
        session, out = make_session(["--prompt", "$ "])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.emu")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("# c\nbad\n\nls ok\n")
            session.run_script(path)
        self.assertEqual(out, ["# c", "$ bad", "bad: command not found",
                               "$ ls ok", "ls: args=['ok']"])

    def test_script_stops_on_exit(self):
        session, out = make_session(["--prompt", "$ "])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.emu")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("exit\nls after\n")
            session.run_script(path)
        self.assertEqual(out, ["$ exit"])

    def test_missing_script_reported(self):
        session, out = make_session()
        session.run_script("/no/such/script")
        self.assertIn("No such file", out[0])

    def test_prompt_placeholders(self):
        session, _out = make_session(["--prompt", "{vfs}@{cwd}> "])
        self.assertEqual(session.prompt_text(), "vfs@/> ")

    def test_motd_printed_at_start(self):
        session, out = make_session()
        session.shell.vfs.root.children["motd"] = VNode("motd", data=b"hi\n")
        session.start()
        self.assertIn("hi", out)

    def test_vfs_info(self):
        session, _out = make_session()
        self.assertIn("files: 0", session.shell.execute("vfs-info"))


if __name__ == "__main__":
    unittest.main()
