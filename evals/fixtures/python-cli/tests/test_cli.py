import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = Path(__file__).resolve().parent / "snapshots"


def run_cli(*args, cwd):
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONIOENCODING": "utf-8", "COLUMNS": "80", "NO_COLOR": "1"}
    return subprocess.run(
        [sys.executable, "-m", "invoicer", *args],
        cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8",
    )


def snapshot(name):
    return (SNAPSHOTS / name).read_text(encoding="utf-8")


class CliTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cwd = tmp.name

    def test_help(self):
        result = run_cli("--help", cwd=self.cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, snapshot("help.txt"))

    def test_csv_invoice_with_discount(self):
        result = run_cli(str(ROOT / "data" / "order.json"), "--output", "invoice.csv", "--discount", "10", cwd=self.cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, snapshot("csv-run.txt"))
        self.assertEqual(Path(self.cwd, "invoice.csv").read_text(encoding="utf-8"), snapshot("invoice.csv"))

    def test_json_invoice_of_small_items(self):
        result = run_cli(str(ROOT / "data" / "stickers.json"), "--format", "json", "--output", "invoice.json", cwd=self.cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, snapshot("json-run.txt"))
        self.assertEqual(Path(self.cwd, "invoice.json").read_text(encoding="utf-8"), snapshot("invoice.json"))

    def test_negative_discount_is_ignored(self):
        result = run_cli(str(ROOT / "data" / "order.json"), "--output", "invoice.csv", "--discount", "-5", cwd=self.cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, snapshot("negative-discount.txt"))

    def test_missing_order_file(self):
        result = run_cli("missing.json", "--output", "invoice.csv", cwd=self.cwd)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, snapshot("missing-file.txt"))

    def test_unknown_format(self):
        result = run_cli(str(ROOT / "data" / "order.json"), "--format", "xml", "--output", "x", cwd=self.cwd)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, snapshot("unknown-format.txt"))


if __name__ == "__main__":
    unittest.main()
