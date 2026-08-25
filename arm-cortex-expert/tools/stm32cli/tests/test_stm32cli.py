# -*- coding: utf-8 -*-
"""stm32cli 单元测试。

运行方式（在 tools/stm32cli 目录下，无需管理员权限）：
    python -X utf8 -m unittest discover -s tests -v

夹具目录固定在工作区 .tmp-tests/ 下（已 gitignore），避免依赖系统 TEMP 权限。
"""
import json
import os
import shutil
import sys
import unittest
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_DIR))

# 工作区根：stm32cli -> tools -> <skill> -> 仓库根
REPO_ROOT = TOOL_DIR.parents[2]
TMP_BASE = REPO_ROOT / ".tmp-tests"

from config import get_latest_db_version, _version_key, get_db_signature
from cache import Cache

FAMILIES_XML = """<?xml version="1.0" encoding="utf-8"?>
<DB>
  <Family Name="STM32F4">
    <SubFamily Name="STM32F407">
      <Mcu RefName="STM32F407VGTx" RPN="STM32F407VG" PackageName="LQFP100">
        <Core>ARM Cortex-M4F</Core>
        <Frequency>168</Frequency>
        <Ram>192</Ram>
        <Flash>1024</Flash>
        <IONb>82</IONb>
      </Mcu>
    </SubFamily>
  </Family>
</DB>"""

_counter = {"n": 0}


def make_test_dir():
    """在仓库 .tmp-tests/ 下创建唯一临时目录（测试结束由调用方清理）。"""
    _counter["n"] += 1
    d = TMP_BASE / f"t{_counter['n']}-{os.getpid()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def drop_dir(d):
    shutil.rmtree(d, ignore_errors=True)


def make_db(root: Path, version: str, freq: int = 168) -> Path:
    d = root / f"DB.{version}" / "db" / "mcu"
    d.mkdir(parents=True, exist_ok=True)
    xml = FAMILIES_XML.replace("<Frequency>168</Frequency>",
                               f"<Frequency>{freq}</Frequency>")
    (d / "families.xml").write_text(xml, encoding="utf-8")
    return root / f"DB.{version}"


class VersionOrderTests(unittest.TestCase):
    def test_numeric_tuple(self):
        self.assertEqual(_version_key("DB.6.10"), (6, 10))
        self.assertEqual(_version_key("DB.6.9"), (6, 9))

    def test_6_10_is_newer_than_6_9(self):
        self.assertGreater(_version_key("DB.6.10"), _version_key("DB.6.9"))

    def test_latest_db_version_picks_highest(self):
        d = make_test_dir()
        try:
            make_db(d, "6.9")
            make_db(d, "6.10")
            self.assertEqual(get_latest_db_version(d).name, "DB.6.10")
        finally:
            drop_dir(d)

    def test_missing_root_returns_none(self):
        self.assertIsNone(get_latest_db_version(Path("Z:/no/such/dir")))


class SignatureTests(unittest.TestCase):
    def setUp(self):
        self.d = make_test_dir()
        make_db(self.d, "6.10")

    def tearDown(self):
        drop_dir(self.d)

    def test_signature_stable_when_untouched(self):
        _, s1 = get_db_signature(self.d)
        _, s2 = get_db_signature(self.d)
        self.assertEqual(s1, s2)

    def test_signature_changes_when_db_file_updates(self):
        _, s1 = get_db_signature(self.d)
        f = self.d / "DB.6.10" / "db" / "mcu" / "families.xml"
        os.utime(f, (1_000_000_000, 1_000_000_000))
        _, s2 = get_db_signature(self.d)
        self.assertNotEqual(s1, s2)

    def test_missing_root_returns_none_signature(self):
        d, s = get_db_signature(Path("Z:/no/such/dir"))
        self.assertIsNone(d)
        self.assertIsNone(s)


class CacheScopeTests(unittest.TestCase):
    def test_keys_scoped_by_signature(self):
        d = make_test_dir()
        try:
            c = Cache(cache_dir=d)
            c.set("chip", "sigA", "STM", data={"v": 1})
            c.set("chip", "sigB", "STM", data={"v": 2})
            self.assertEqual(c.get("chip", "sigA", "STM")["v"], 1)
            self.assertEqual(c.get("chip", "sigB", "STM")["v"], 2)
        finally:
            drop_dir(d)


class ChipHandlerTests(unittest.TestCase):
    def setUp(self):
        self.d = make_test_dir()
        make_db(self.d, "6.10")
        self.cache_dir = make_test_dir()

    def tearDown(self):
        drop_dir(self.d)
        drop_dir(self.cache_dir)

    def _cache(self):
        return Cache(cache_dir=self.cache_dir)

    def test_handle_chip_ok(self):
        from commands.chip import handle_chip
        r = handle_chip("STM32F407VGTx", db_path=self.d, cache=self._cache())
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["data"]["name"], "STM32F407VGTx")

    def test_handle_chip_not_found(self):
        from commands.chip import handle_chip
        r = handle_chip("NOSUCH123", db_path=self.d, cache=self._cache())
        self.assertEqual(r["status"], "error")
        self.assertEqual(r["error"]["code"], "MCU_NOT_FOUND")

    def test_cache_invalidated_when_db_updates(self):
        """同一 Cache 实例下，数据库内容更新后必须拿到新结果而非旧缓存。"""
        from commands.chip import handle_chip
        c = self._cache()
        r1 = handle_chip("STM32F407VGTx", db_path=self.d, cache=c)
        self.assertEqual(r1["data"]["freq_mhz"], 168)
        f = self.d / "DB.6.10" / "db" / "mcu" / "families.xml"
        f.write_text(FAMILIES_XML.replace("<Frequency>168</Frequency>",
                                          "<Frequency>200</Frequency>"), encoding="utf-8")
        os.utime(f, (1_000_000_000, 1_000_000_000))
        r2 = handle_chip("STM32F407VGTx", db_path=self.d, cache=c)
        self.assertEqual(r2["data"]["freq_mhz"], 200)


class CliExitCodeTests(unittest.TestCase):
    """子进程级验证：--help 正常、错误返回非零退出码、选项前后位置均合法。"""

    def _run(self, *cli_args):
        import subprocess
        env = dict(os.environ)
        env["PYTHONUTF8"] = "1"
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(TOOL_DIR / "stm32cli.py"), *cli_args],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(TOOL_DIR), timeout=60, env=env,
        )

    def setUp(self):
        self.d = make_test_dir()
        make_db(self.d, "6.10")

    def tearDown(self):
        drop_dir(self.d)

    def test_help_exits_zero(self):
        r = self._run("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("usage", r.stdout.lower())

    def test_global_option_before_subcommand(self):
        r = self._run("--db-path", str(self.d), "chip", "NOSUCH123")
        self.assertNotEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["error"]["code"], "MCU_NOT_FOUND")

    def _assert_ok(self, r):
        if r.returncode != 0:
            self.fail(f"rc={r.returncode}\n--STDOUT--\n{r.stdout}\n--STDERR--\n{r.stderr}")

    def test_global_option_after_subcommand(self):
        r = self._run("chip", "--db-path", str(self.d), "STM32F407VGTx")
        self._assert_ok(r)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["data"]["name"], "STM32F407VGTx")

    def test_error_exits_nonzero_with_json(self):
        r = self._run("chip", "NOSUCH123", "--db-path", str(self.d))
        self.assertNotEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["status"], "error")

    def test_missing_arg_exits_nonzero(self):
        r = self._run("clock", "--db-path", str(self.d))
        self.assertNotEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["error"]["code"], "MISSING_ARG")


if __name__ == "__main__":
    unittest.main()
