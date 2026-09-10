"""Behavioral tests for the offline linter, not tests of target firmware."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("state_linter", SKILL / "scripts" / "check_state_model.py")
linter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(linter)


def example(name="reconfigure-model.json"):
    return json.loads((SKILL / "assets" / name).read_text(encoding="utf-8"))


def codes(report):
    return {item["code"] for item in report["issues"]}


class StateModelTests(unittest.TestCase):
    def test_good_example_has_timeout_fallback_to_uncertain_terminal(self):
        report = linter.analyze(example())
        self.assertEqual(report["status"], "pass")
        self.assertFalse(report["issues"])
        self.assertEqual(report["timeout_chain_budgets"]["START"],
                         {"to": "INDETERMINATE", "declared_wait_ms": 300})

    def test_success_exit_does_not_hide_timeout_cycle(self):
        report = linter.analyze(example("stuck-model.json"))
        self.assertEqual(report["status"], "fail")
        self.assertIn("TIMEOUT_CYCLE", codes(report))
        self.assertNotIn("NO_BOUNDARY_PATH", codes(report))
        self.assertNotIn("WAIT_ACK", report["timeout_chain_budgets"])

    def test_success_edge_without_timeout_is_insufficient(self):
        model = example()
        del model["states"]["START"]["timeout"]
        self.assertIn("MISSING_TIMEOUT", codes(linter.analyze(model)))

    def test_closed_region_has_no_boundary_and_a_cycle(self):
        model = example("stuck-model.json")
        model["transitions"] = []
        report = linter.analyze(model)
        self.assertTrue({"NO_BOUNDARY_PATH", "TIMEOUT_CYCLE", "UNREACHABLE"} <= codes(report))

    def test_transient_dead_end(self):
        model = {"version": 1, "initial": "WAIT", "states": {"WAIT": {"kind": "transient"}},
                 "transitions": []}
        self.assertTrue({"MISSING_TIMEOUT", "NO_BOUNDARY_PATH"} <= codes(linter.analyze(model)))

    def test_idle_can_remain_stable_forever(self):
        model = {"version": 1, "initial": "IDLE", "states": {"IDLE": {"kind": "stable"}},
                 "transitions": [{"from": "IDLE", "event": "QUERY", "to": "IDLE"}]}
        self.assertEqual(linter.analyze(model)["status"], "pass")

    def test_terminal_cannot_reopen(self):
        model = example()
        model["transitions"].append({"from": "SUCCEEDED", "event": "LATE_FAILURE", "to": "CONTAIN"})
        self.assertIn("TERMINAL_OUTGOING", codes(linter.analyze(model)))

    def test_retry_loop_warns_even_when_timeout_graph_terminates(self):
        model = example()
        model["transitions"].append({"from": "START", "event": "BUSY", "to": "START"})
        report = linter.analyze(model)
        self.assertIn("TRANSIENT_CYCLE", codes(report))
        self.assertNotIn("TIMEOUT_CYCLE", codes(report))
        self.assertEqual(report["status"], "pass")

    def test_guard_is_not_a_proof_of_reachability(self):
        model = example()
        model["transitions"][0]["guard"] = "false"
        self.assertIn("GUARDS_ABSTRACTED", codes(linter.analyze(model)))

    def test_shortest_witness_identifies_timeout_only_entry(self):
        model = example()
        model["states"]["CONTAIN"]["timeout"]["to"] = "CONTAIN"
        issue = next(i for i in linter.analyze(model)["issues"] if i["code"] == "TIMEOUT_CYCLE")
        self.assertEqual(len(issue["witness"]), 2)
        self.assertEqual(issue["witness"][0]["from"], "IDLE")
        self.assertEqual(issue["witness"][-1]["to"], "CONTAIN")
        self.assertEqual(issue["cycle"], ["CONTAIN", "CONTAIN"])

    def test_rejects_invalid_timeout_values(self):
        for value in (0, -1, True, 1.5, "100", None):
            with self.subTest(value=value):
                model = example()
                model["states"]["START"]["timeout"]["after_ms"] = value
                with self.assertRaises(linter.ModelError):
                    linter.analyze(model)

    def test_schema_failures_are_explicit(self):
        mutations = [
            lambda m: m.update(initial="MISSING"),
            lambda m: m.update(version=True),
            lambda m: m["states"]["START"]["timeout"].update(to="MISSING"),
            lambda m: m["transitions"][0].update(to="MISSING"),
            lambda m: m["transitions"].append(copy.deepcopy(m["transitions"][0])),
            lambda m: m["states"]["START"].update(timeot={}),
            lambda m: m["states"]["IDLE"].update(timeout={"after_ms": 1, "to": "START"}),
            lambda m: m["transitions"][0].update(event="@timeout"),
            lambda m: m.update(states=[]),
        ]
        for change in mutations:
            with self.subTest(change=change):
                model = example()
                change(model)
                with self.assertRaises(linter.ModelError):
                    linter.analyze(model)

    def test_long_acyclic_chain_without_python_recursion(self):
        states = {f"S{i}": {"kind": "transient", "timeout": {"after_ms": 1, "to": f"S{i+1}"}}
                  for i in range(999)}
        states["S999"] = {"kind": "terminal"}
        report = linter.analyze({"version": 1, "initial": "S0", "states": states, "transitions": []})
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["timeout_chain_budgets"]["S0"]["declared_wait_ms"], 999)

    def test_cli_exit_codes_and_json(self):
        for filename, expected in (("reconfigure-model.json", 0), ("stuck-model.json", 1)):
            with self.subTest(filename=filename), contextlib.redirect_stdout(io.StringIO()) as out:
                code = linter.main([str(SKILL / "assets" / filename), "--json"])
            self.assertEqual(code, expected)
            self.assertIn(json.loads(out.getvalue())["status"], ("pass", "fail"))

    def test_cli_invalid_missing_duplicate_and_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.json"
            for raw in ("{", '{"version":1,"version":1}', '[1]', '{"version":true}'):
                path.write_text(raw, encoding="utf-8")
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(linter.main([str(path), "--json"]), 2)
                self.assertEqual(json.loads(out.getvalue())["status"], "invalid")
            path.write_text(json.dumps(example()), encoding="utf-8-sig")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(linter.main([str(path)]), 0)
                self.assertEqual(linter.main([str(Path(tmp) / "absent.json")]), 2)

    def test_strict_gate_blocks_warnings_without_reclassifying_graph(self):
        for warning in ("loop", "guard", "unreachable"):
            with self.subTest(warning=warning), tempfile.TemporaryDirectory() as tmp:
                model = example()
                if warning == "loop":
                    model["transitions"].append({"from": "START", "event": "BUSY", "to": "START"})
                elif warning == "guard":
                    model["transitions"][0]["guard"] = "false"
                else:
                    model["states"]["UNUSED"] = {"kind": "stable"}
                path = Path(tmp) / "model.json"
                path.write_text(json.dumps(model), encoding="utf-8")
                for flags, expected in (([], 0), (["--strict"], 1)):
                    with contextlib.redirect_stdout(io.StringIO()) as out:
                        code = linter.main([str(path), "--json", *flags])
                    report = json.loads(out.getvalue())
                    self.assertEqual(code, expected)
                    self.assertEqual(report["status"], "pass")
                    self.assertEqual(report["gate_status"], "fail" if expected else "pass")
                    self.assertTrue(report["issues"])

    def test_strict_gate_keeps_clean_error_and_invalid_exit_codes(self):
        for filename, expected in (("reconfigure-model.json", 0), ("stuck-model.json", 1),
                                   ("missing-model.json", 2)):
            with self.subTest(filename=filename), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(linter.main([str(SKILL / "assets" / filename), "--strict"]), expected)

    def test_strict_text_exposes_failed_gate_for_warning_only_model(self):
        model = example()
        model["transitions"][0]["guard"] = "false"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(linter.main([str(path), "--strict"]), 1)
            self.assertIn("GATE FAIL", out.getvalue())


if __name__ == "__main__":
    unittest.main()
